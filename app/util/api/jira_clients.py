import json
import string
from selenium.common.exceptions import WebDriverException

from util.api.abstract_clients import RestClient, JSM_EXPERIMENTAL_HEADERS
from selenium_ui.conftest import retry

BATCH_SIZE_BOARDS = 1000
BATCH_SIZE_ISSUES = 1000


class JiraRestClient(RestClient):

    def get_boards(self, start_at=0, max_results=100, board_type=None, name=None, project_key_or_id=None):
        """
        Returns all boards. This only includes boards that the user has permission to view.
        :param start_at: The starting index of the returned boards. Base index: 0.
        :param max_results: The maximum number of boards to return per page. Default: 100.
        :param board_type: Filters results to boards of the specified type. Valid values: scrum, kanban.
        :param name: Filters results to boards that match or partially match the specified name.
        :param project_key_or_id: Filters results to boards that are relevant to a project.
        Relevance meaning that the jql filter defined in board contains a reference to a project.
        :return: Returns the requested boards, at the specified page of the results.
        """

        loop_count = max_results // BATCH_SIZE_BOARDS + 1
        last_loop_remainder = max_results % BATCH_SIZE_BOARDS

        boards_list = list()
        max_results = BATCH_SIZE_BOARDS if max_results > BATCH_SIZE_BOARDS else max_results

        while loop_count > 0:
            api_url = f"{self.host}/rest/agile/1.0/board?startAt={start_at}&maxResults={max_results}"
            if board_type:
                api_url += f"&type={board_type}"
            if name:
                api_url += f"&name={name}"
            if project_key_or_id:
                api_url += f"&projectKeyOrID={project_key_or_id}"

            response = self.get(api_url, "Could not retrieve boards")

            boards_list.extend(response.json()['values'])
            loop_count -= 1
            start_at += len(response.json()['values'])
            if loop_count == 1:
                max_results = last_loop_remainder

        return boards_list

    @retry()
    def get_users(self, username='.', include_active=True, include_inactive=False):
        """
        Starting from Jira 10 there is no way to get more than 100 users with get_users() API
        startAt param will be deprecated in Jira 10.3+
        """
        max_results = 100

        api_url = f'{self.host}/rest/api/2/user/search?username={username}' \
                  f'&maxResults={max_results}' \
                  f'&includeActive={include_active}' \
                  f'&includeInactive={include_inactive}'
        response = self.get(api_url, "Could not retrieve users")
        users_list = response.json()

        return users_list

    @retry()
    def get_users_by_name_search(self, username, users_count, include_active=True, include_inactive=False):
        """
        Starting from Jira 10 there is no way to get more than 100 users with get_users() API
        Getting more than 100 users by batch search.
        """
        print(f"INFO: Users search. Prefix: '{username}', users_count: {users_count}")
        perf_users = list()

        first_100 = self.get_users(username=username, include_active=True, include_inactive=False)
        if users_count <= 100 or len(first_100) < 100:
            perf_users = first_100[:users_count]
        else:
            name_start_list = list(string.digits + "_" + string.ascii_lowercase)
            for i in name_start_list:
                users_batch = self.get_users(username=username+i, include_active=True, include_inactive=False)
                if len(users_batch) == 100:
                    print(f"Warning: found 100 users starts with: {username+i}. Checking if there are more.")
                    users_batch = self.get_users_by_name_search(username=username+i,
                                                                users_count=users_count-len(perf_users))
                perf_users.extend(users_batch)

                # get rid of any duplicates by creating a set from json objects
                set_of_jsons = {json.dumps(d, sort_keys=True) for d in perf_users}
                perf_users = [json.loads(t) for t in set_of_jsons]
                print(f"INFO: Current found users count: {len(perf_users)}")

                if len(perf_users) >= users_count:
                    perf_users = perf_users[:users_count]
                    break
        return perf_users

    @retry()
    def issues_search(self, jql='order by key', start_at=0, max_results=1000, fields=None):
        """
        Searches for issues using JQL.
        :param jql: a JQL query string
        :param start_at: the index of the first issue to return (0-based)
        :param max_results: the maximum number of issues to return (defaults to 50).
        :param fields: the list of fields to return for each issue. By default, all navigable fields are returned.
        *all - include all fields
        *navigable - include just navigable fields
        summary,comment - include just the summary and comments
        -description - include navigable fields except the description (the default is *navigable for search)
        *all,-comment - include everything except comments
        :return: Returns the requested issues
        """

        loop_count = max_results // BATCH_SIZE_ISSUES + 1
        issues = list()
        last_loop_remainder = max_results % BATCH_SIZE_ISSUES
        api_url = f'{self.host}/rest/api/2/search'

        while loop_count > 0:

            body = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "fields": ['id'] if fields is None else fields
            }

            response = self.post(api_url, "Could not retrieve issues", body=body)

            current_issues = response.json()['issues']
            issues.extend(current_issues)
            start_at += len(current_issues)
            loop_count -= 1
            if loop_count == 1:
                max_results = last_loop_remainder

        return issues

    @retry()
    def get_total_issues_count(self, jql: str = ''):
        api_url = f'{self.host}/rest/api/2/search'
        body = {"jql": jql if jql else "order by key",
                "startAt": 0,
                "maxResults": 0,
                "fields": ["summary"]
                }
        response = self.post(api_url, "Could not retrieve issues", body=body)
        return response.json().get('total', 0)

    def create_user(self, display_name=None, email=None, name='', password='', application_keys=None):
        """
        Creates a user. This resource is retained for legacy compatibility.
        As soon as a more suitable alternative is available this resource will be deprecated.
        :param name: The username for the user. This property is deprecated because of privacy changes.
        :param password: A password for the user. If a password is not set, a random password is generated.
        :param email: tThe email address for the user. Required.
        :param display_name: The display name for the user. Required.
        :param application_keys
        :return: Returns the created user.
        """
        api_url = self._host + "/rest/api/2/user"
        payload = {
            "name": name,
            "password": password,
            "emailAddress": email or name + '@localdomain.com',
            "displayName": display_name or name
        }

        if application_keys is not None:
            payload["applicationKeys"] = application_keys

        response = self.post(api_url, "Could not create user", body=payload)

        return response.json()

    def get_all_projects(self):
        """
        :return: Returns the projects list of all project types - all categories
        """
        api_url = f'{self.host}/rest/api/2/project'
        response = self.get(api_url, 'Could not get the list of projects')

        return response.json()

    def get_server_info(self):
        api_url = f'{self.host}/rest/api/2/serverInfo'
        response = self.get(api_url, 'Could not get the server information')

        return response.json()

    def get_nodes(self):
        api_url = f'{self.host}/rest/api/2/cluster/nodes'
        response = self.get(api_url, 'Could not get Jira nodes count', expected_status_codes=[200, 405])
        if response.status_code == 405 and 'This Jira instance is not clustered' in response.text:
            return 'Server'
        nodes = [node['nodeId'] for node in response.json() if node['state'] == "ACTIVE" and node['alive']]
        return nodes

    def get_system_info_page(self):
        login_url = f'{self.host}/login.jsp'
        auth_url = f'{self.host}/secure/admin/WebSudoAuthenticate.jspa'
        auth_body = {
            'webSudoDestination': '/secure/admin/ViewSystemInfo.jspa',
            'webSudoIsPost': False,
            'webSudoPassword': self.password
        }
        self.post(login_url, error_msg='Could not login in')
        auth_body['atl_token'] = self.session.cookies.get_dict()['atlassian.xsrf.token']
        system_info_html = self._session.post(auth_url, data=auth_body, verify=self.verify)
        return system_info_html.content.decode("utf-8")

    def get_available_processors(self):
        try:
            node_id = self.get_nodes()[0]
            api_url = f'{self.host}/rest/atlassian-cluster-monitoring/cluster/suppliers/data/com.atlassian.cluster' \
                      f'.monitoring.cluster-monitoring-plugin/runtime-information/{node_id}'
            response = self.get(api_url, "Could not get Available Processors information")
            processors = response.json()['data']['rows']['availableProcessors'][1]
        except Exception as e:
            print(f"Warning: Could not get Available Processors information. Error: {e}")
            return 'N/A'
        return processors

    def get_locale(self):
        api_url = f'{self.host}/rest/api/2/myself'
        user_properties = self.get(api_url, "Could not retrieve user")
        return user_properties.json()['locale']

    def get_applications_properties(self):
        api_url = f'{self.host}/rest/api/2/application-properties'
        app_properties = self.get(api_url, "Could not retrieve application properties")
        return app_properties.json()

    def check_rte_status(self):
        # Safe check for RTE status. Return RTE status or return default value (True).
        try:
            app_prop = self.get_applications_properties()
            rte = [i['value'] for i in app_prop if i['id'] == 'jira.rte.enabled']
            if rte:
                return rte[0] == 'true'
            else:
                raise Exception("RTE status was nof found in application properties.")
        except (Exception, WebDriverException) as e:
            print(f"Warning: failed to get RTE status. Returned default value: True. Error: {e}")
            return True

    def get_user_permissions(self):
        api_url = f'{self.host}/rest/api/2/mypermissions'
        app_properties = self.get(api_url, "Could not retrieve user permissions")
        return app_properties.json()

    def get_deployment_type(self):
        html_pattern = 'com.atlassian.dcapt.deployment=terraform'
        jira_system_page = self.get_system_info_page()
        if jira_system_page.count(html_pattern):
            return 'terraform'
        return 'other'

    @retry()
    def get_status(self):
        api_url = f'{self.host}/status'
        status = self.get(api_url, "Could not get status")
        if status.ok:
            return status.text
        else:
            print(f"Warning: failed to get {api_url}: Error: {e}")
            return False

    def get_license_details(self):
        login_url = f'{self.host}/login.jsp'
        auth_url = f'{self.host}/secure/admin/WebSudoAuthenticate.jspa'
        auth_body = {
            'webSudoDestination': '/secure/admin/ViewSystemInfo.jspa',
            'webSudoIsPost': False,
            'webSudoPassword': self.password
        }
        self.post(login_url, error_msg='Could not login in')
        auth_body['atl_token'] = self.session.cookies.get_dict()['atlassian.xsrf.token']
        self._session.post(auth_url, data=auth_body)
        api_url = f"{self.host}/rest/plugins/applications/1.0/installed/jira-software/license"
        self.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,' \
                                 'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
        r = self.get(api_url, "Could not retrieve license details")
        return r.json()
