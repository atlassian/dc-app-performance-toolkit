from lxml import html

from util.api.abstract_clients import RestClient
from selenium_ui.conftest import retry

BATCH_SIZE_SEARCH = 500


class BambooClient(RestClient):

    def get_build_plans(self, start=0, max_result=100):
        loop_count = max_result // BATCH_SIZE_SEARCH + 1
        content = list()
        last_loop_remainder = max_result % BATCH_SIZE_SEARCH
        max_result = BATCH_SIZE_SEARCH if max_result > BATCH_SIZE_SEARCH else max_result

        while loop_count > 0:
            if not max_result:
                break
            api_url = (
                    self.host + f'/rest/api/latest/search/plans?start-index={start}'
                                f'&max-result={max_result}'
            )
            request = self.get(api_url, "Could not retrieve build plans")
            if request.json()['start-index'] != start:
                break
            content.extend(request.json()['searchResults'])

            loop_count -= 1
            if loop_count == 1:
                max_result = last_loop_remainder

            start += len(request.json()['searchResults'])

        return content

    def get_build_plans_results(self, build_plan_id, start=0, max_result=100):
        loop_count = max_result // BATCH_SIZE_SEARCH + 1
        content = list()
        last_loop_remainder = max_result % BATCH_SIZE_SEARCH
        max_result = BATCH_SIZE_SEARCH if max_result > BATCH_SIZE_SEARCH else max_result

        while loop_count > 0:
            if not max_result:
                break
            api_url = (
                    self.host + f'/rest/api/latest/result/{build_plan_id}?start-index={start}'
                                f'&max-result={max_result}'
            )
            request = self.get(api_url, "Could not retrieve build plans result")
            if request.json()['results']['start-index'] != start:
                break
            content.extend(request.json()['results']['result'])

            loop_count -= 1
            if loop_count == 1:
                max_result = last_loop_remainder

            start += len(request.json()['results']['result'])

        return content

    def get_build_plan_results(self, build_run_id):
        request = self.get(f'{self.host}/rest/api/latest/result/{build_run_id}',
                           "Could not retrieve build plan result")

        return request.json()

    @retry()
    def get_build_job_results(self, build_job_id):
        request = self.get(f'{self.host}/rest/api/latest/result/{build_job_id}',
                           "Could not retrieve build job results")

        return request.json()

    def get_users(self, limit):
        """
        Retrieve a page of users. The authenticated user must have restricted
        administrative permission or higher to use this resource.
        :param start: The starting index of the returned users. Base index: 0.
        :param limit: The maximum number of users to return per page. Default: 25.
        """
        request = self.get(f'{self.host}/rest/api/latest/admin/users?limit={limit}',
                           error_msg="Can not retrieve users")
        content = request.json()
        return content['results']

    def get_projects(self, start=0, max_result=100):
        loop_count = max_result // BATCH_SIZE_SEARCH + 1
        content = list()
        last_loop_remainder = max_result % BATCH_SIZE_SEARCH
        max_result = BATCH_SIZE_SEARCH if max_result > BATCH_SIZE_SEARCH else max_result

        while loop_count > 0:
            if not max_result:
                break
            api_url = (
                    self.host + f'/rest/api/latest/project?start-index={start}'
                                f'&max-result={max_result}'
            )
            request = self.get(api_url, "Could not retrieve projects")
            if request.json()['projects']['start-index'] != start:
                break
            content.extend(request.json()['projects']['project'])

            loop_count -= 1
            if loop_count == 1:
                max_result = last_loop_remainder

            start += len(request.json()['projects']['project'])

        return content

    def create_user(self, name, password):
        """
        Create a new user. The authenticated user must have restricted administrative
        permission or higher to use this resource.
        :param name: username to create.
        :param fullName: full user name.
        :email: email address.
        :password: password.
        :passwordConfirm: confirm password.
        """
        api_url = f'{self.host}/rest/api/latest/admin/users'
        payload = {"name": name,
                   "fullName": name,
                   "email": f'{name}@example.com',
                   "password": password,
                   "passwordConfirm": password}
        self.post(api_url, body=payload, error_msg="Could not create user")
        return {'name': name}

    def start_build_plan(self, plan_key):
        api_url = f'{self.host}/rest/api/latest/queue/{plan_key}'
        r = self.post(api_url, error_msg=f"Could not start the plan {plan_key}")
        return r.json()

    def get_build_plan_status(self, plan_key):
        api_url = f'{self.host}/rest/api/latest/plan/{plan_key}'
        r = self.get(api_url, error_msg=f"Could not get plan {plan_key} status")
        return r.json()

    def get_build_results(self, plan_key, run_number: int = None):
        api_url = f'{self.host}/rest/api/latest/result/{plan_key}'
        if run_number:
            api_url = f'{self.host}/rest/api/latest/result/{plan_key}-{run_number}'
        r = self.get(api_url, error_msg=f"Could not get plan {plan_key} results")
        return r.json()

    def get_remote_agents(self, online=True):
        api_url = f'{self.host}/rest/api/latest/agent/remote'
        if online:
            api_url = f'{self.host}/rest/api/latest/agent/remote?online=True'
        r = self.get(api_url, error_msg="Could not get online agents")
        return r.json()

    def get_server_info(self):
        r = self.get(f'{self.host}/rest/applinks/1.0/manifest', error_msg="Could not get Bamboo server info")
        return r.json()

    def get_system_page(self):
        login_url = f'{self.host}/userlogin.action'
        auth_url = f'{self.host}/admin/webSudoSubmit.action'
        tsv_auth_url = f'{self.host}/rest/tsv/1.0/authenticate'

        legacy_login_body = {
            'os_username': self.user,
            'os_password': self.password,
            'os_destination': '/admin/systemInfo.action',
            'atl_token': '',
            'save': 'Log in'
        }

        tsv_login_body = {
            'username': self.user,
            'password': self.password,
            'rememberMe': True,
            'targetUrl': ''
        }

        auth_body = {
            'web_sudo_destination': '/admin/systemInfo.action',
            'save': 'Submit',
            'password': self.password
        }

        login_page_response = self.session.get(login_url)
        if login_page_response.status_code == 200:
            login_page_content = login_page_response.text
            is_legacy_login_form = 'loginForm' in login_page_content
        else:
            raise Exception(f"Failed to fetch login page. Status code: {login_page_response.status_code}")

        self.headers['X-Atlassian-Token'] = 'no-check'
        if is_legacy_login_form:
            r = self.session.post(url=login_url, params=legacy_login_body, headers=self.headers)
            content = r.content.decode("utf-8")
            # Bamboo version 9 does not have web sudo auth
            if "System information" in content:
                print("INFO: No web sudo auth")
                return content
            elif "Administrator Access" in content:
                print("INFO: Web sudo page detected")
            else:
                print(f"Warning: Unexpected login page: Content {content}")
        else:
            self.session.post(url=tsv_auth_url, json=tsv_login_body)

        system_info_html = self.session.post(url=auth_url, params=auth_body, headers=self.headers)
        content = system_info_html.content.decode("utf-8")
        if "System information" not in content:
            print(f"Warning: failed to get System information page: Content {content}")
        return content

    def get_available_processors(self):
        try:
            processors = None
            page = self.get_system_page()
            tree = html.fromstring(page)
            try:
                processors = tree.xpath('//*[@id="systemInfo_availableProcessors"]/text()')[0]
            except Exception as e:
                print(f"Warning: Could not parse number of Bamboo available processors: {e}")
            return processors
        except Exception as e:
            print(f"Warning: Could not get Available Processors information. Error: {e}")
            return 'N/A'

    def get_nodes_count(self):
        r = self.get(f'{self.host}/rest/api/latest/server/nodes', error_msg="Could not get Bamboo nodes count")
        return len(r.json()["nodeStatuses"])

    def get_deployment_type(self):
        bamboo_system_info_html = self.get_system_page()
        html_pattern = 'com.atlassian.dcapt.deployment=terraform'
        if bamboo_system_info_html.count(html_pattern):
            return 'terraform'
        return 'other'

    @retry()
    def get_status(self):
        api_url = f'{self.host}/rest/api/latest/status'
        status = self.get(api_url, "Could not get status")
        if status.ok:
            return status.text
        else:
            print(f"Warning: failed to get {api_url}: Error: {e}")
            return False
