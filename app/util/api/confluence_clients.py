import xmlrpc.client
from selenium_ui.conftest import retry

from util.api.abstract_clients import RestClient, Client
from lxml import html

BATCH_SIZE_SEARCH = 500


class ConfluenceRestClient(RestClient):

    def get_content(self, start=0, limit=100, type="page", expand="space"):
        """
        Returns all content. This only includes pages that the user has permission to view.
        :param start: The starting index of the returned boards. Base index: 0.
        :param limit: The maximum number of boards to return per page. Default: 50.
        :param type: the content type to return. Default value: page. Valid values: page, blogpost.
        :param expand: Responds with additional values. Valid values: space,history,body.view,metadata.label
        :return: Returns the requested content, at the specified page of the results.
        """
        BATCH_SIZE_SEARCH = 200
        loop_count = limit // BATCH_SIZE_SEARCH + 1
        content = list()
        last_loop_remainder = limit % BATCH_SIZE_SEARCH
        limit = BATCH_SIZE_SEARCH if limit > BATCH_SIZE_SEARCH else limit

        while loop_count > 0:
            api_url = (
                self.host + f'/rest/api/content/?type={type}'
                f'&start={start}'
                f'&limit={limit}'
                f'&expand={expand}'
            )
            request = self.get(api_url, "Could not retrieve content")

            content.extend(request.json()['results'])
            if len(content) == 0:
                raise Exception(f"Content with type {type} is not found.")

            loop_count -= 1
            if loop_count == 1:
                limit = last_loop_remainder

            start += len(request.json()['results'])

        return content

    @retry()
    def get_content_search(self, start=0, limit=100, cql=None, expand="space"):
        """
        Fetch a list of content using the Confluence Query Language (CQL).
        :param start: The starting index of the returned boards. Base index: 0.
        :param limit: The maximum number of boards to return per page. Default: 50.
        :param cql: Filters results to boards of the specified type. Valid values: page, blogpost
        :param expand: Responds with additional values. Valid values: space,history,body.view,metadata.label
        :return: Returns the requested content, at the specified page of the results.
        """
        BATCH_SIZE_SEARCH = 200
        loop_count = limit // BATCH_SIZE_SEARCH + 1
        content = list()
        last_loop_remainder = limit % BATCH_SIZE_SEARCH
        limit = BATCH_SIZE_SEARCH if limit > BATCH_SIZE_SEARCH else limit

        while loop_count > 0:
            api_url = (
                self.host + f'/rest/api/content/search?cql={cql}'
                f'&start={start}'
                f'&limit={limit}'
                f'&expand={expand}'
            )
            request = self.get(api_url, "Could not retrieve content")

            content.extend(request.json()['results'])
            if len(content) == 0:
                raise Exception(f"Content with cql '{cql}' not found.")

            loop_count -= 1
            if loop_count == 1:
                limit = last_loop_remainder

            start += len(request.json()['results'])

        return content

    def get_users(self, prefix, count):
        users_list = self.search(f"user~{prefix}", limit=count)
        return users_list

    def get_confluence_version(self):
        api_url = f'{self.host}/rest/applinks/1.0/manifest'
        response = self.get(api_url, 'Could not get Confluence manifest')

        return response.json()['version']

    def search(self, cql, cqlcontext=None, expand=None, start=0, limit=500):
        """
        Fetch a list of content using the Confluence Query Language (CQL).
        :param cql: a cql query string to use to locate content
        :param cqlcontext: the context to execute a cql search in, this is the json serialized form of SearchContext
        :param expand: a comma separated list of properties to expand on the content
        :param start: the start point of the collection to return
        :param limit: the limit of the number of items to return, this may be restricted by fixed system limits
        :return:
        """
        loop_count = limit // BATCH_SIZE_SEARCH + 1
        last_loop_remainder = limit % BATCH_SIZE_SEARCH

        search_results_list = list()
        limit = BATCH_SIZE_SEARCH if limit > BATCH_SIZE_SEARCH else limit

        while loop_count > 0:
            api_url = f'{self.host}/rest/api/search?cql={cql}&start={start}&limit={limit}'
            response = self.get(api_url, "Search failed")

            search_results_list.extend(response.json()['results'])
            loop_count -= 1
            start += len(response.json())
            if loop_count == 1:
                limit = last_loop_remainder

        return search_results_list

    @retry()
    def is_remote_api_enabled(self):
        api_url = f'{self.host}/rpc/xmlrpc'
        response = self.get(
            api_url, error_msg='Confluence Remote API (XML-RPC & SOAP) is disabled. '
            'For further processing enable Remote API via '
            'General Configuration - Further Configuration - Remote API')
        return response.status_code == 200

    def get_confluence_nodes(self):
        response = self.get(
            f'{self.host}/rest/zdu/cluster',
            error_msg='Could not get Confluence nodes count via API',
            expected_status_codes=[
                200,
                403,
                500])
        if response.status_code == 403 and 'clustered installation' in response.text:
            return 'Server'
        nodes = [node['id'] for node in response.json()['nodes']]
        return nodes

    def get_available_processors(self):
        try:
            nodes = self.get_confluence_nodes()
            if nodes == 'Server':
                return 'Server'
            node_id = self.get_confluence_nodes()[0]
            api_url = f'{self.host}/rest/atlassian-cluster-monitoring/cluster/suppliers/data/com.atlassian.cluster' \
                      f'.monitoring.cluster-monitoring-plugin/runtime-information/{node_id}'
            response = self.get(
                api_url, "Could not get Available Processors information")
            processors = response.json(
            )['data']['rows']['availableProcessors'][1]
        except Exception as e:
            print(
                f"Warning: Could not get Available Processors information. Error: {e}")
            return 'N/A'
        return processors

    def get_total_pages_count(self):
        api_url = f"{self.host}/rest/api/search?cql=type=page"
        response = self.get(api_url, 'Could not get issues count')
        return response.json().get('totalSize', 0)

    def get_collaborative_editing_status(self):
        api_url = f'{self.host}/rest/synchrony-interop/status'
        response = self.get(
            api_url, error_msg='Could not get collaborative editing status')
        return response.json()

    def get_locale(self):
        language = None
        page = self.get(
            f"{self.host}/index.action#all-updates",
            "Could not get page content.")
        tree = html.fromstring(page.content)
        try:
            language = tree.xpath(
                './/meta[@name="ajs-user-locale"]/@content')[0]
        except Exception as error:
            print(f"Warning: Could not get user locale: {error}")
        return language

    def get_groups_membership(self, username):
        api_url = f'{self.host}/rest/api/user/memberof?username={username}'
        response = self.get(api_url, error_msg='Could not get group members')
        groups = [group['name'] for group in response.json()['results']]
        return groups

    def get_system_info_page(self):
        login_url = f'{self.host}/dologin.action'
        auth_url = f'{self.host}/doauthenticate.action'
        tsv_auth_url = f'{self.host}/rest/tsv/1.0/authenticate'
        tsv_login_body = {
            'username': self.user,
            'password': self.password,
            'rememberMe': True,
            'targetUrl': ''
        }

        auth_body = {
            'authenticate': 'Confirm',
            'destination': '/admin/systeminfo.action',
            'password': self.password,
        }

        login_page_response = self.session.get(login_url)
        if login_page_response.status_code == 200:
            login_page_content = login_page_response.text
            is_legacy_login_form = 'loginform' in login_page_content
        else:
            raise Exception(f"Failed to fetch login page. Status code: {login_page_response.status_code}")

        if is_legacy_login_form:
            self.session.post(url=login_url)
        else:
            self.session.post(url=tsv_auth_url, json=tsv_login_body)

        system_info_html = self.session.post(url=auth_url, data=auth_body, headers={'X-Atlassian-Token': 'no-check'}, verify=self.verify)
        return system_info_html.content.decode("utf-8")

    def get_deployment_type(self):
        html_pattern = 'deployment=terraform'
        confluence_system_page = self.get_system_info_page()
        if confluence_system_page.count(html_pattern):
            return 'terraform'
        return 'other'

    def get_node_ip(self, node_id: str) -> str:
        if node_id != "SERVER":
            return self.get(
                url=f"{self.host}/rest/zdu/nodes/{node_id}",
                expected_status_codes=[200],
                error_msg=f"Cannot get {node_id} node IP",
            ).json().get("ipAddress")
        else:
            return ""

    def create_user(self, username, password):
        create_user_url = f'{self.host}/rest/api/admin/user'
        payload = {
            "userName": username,
            "password": password,
            "email": f'{username}@test.com',
            "notifyViaEmail": False,
            "fullName": username.capitalize()
        }
        r = self.post(
            url=create_user_url,
            body=payload,
            error_msg='ERROR: Could not create user')
        return r.json()

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
        api_url = f'{self.host}/rest/license/1.0/license/details'
        r = self.get(api_url, "Could not get license details")
        return r.json()

    def get_license_remaining_seats(self):
        api_url = f'{self.host}/rest/license/1.0/license/remainingSeats'
        r = self.get(api_url, "Could not get license remaining seats")
        return r.json()


class ConfluenceRpcClient(Client):

    def create_user(self, username=None, password=None):
        """
        Creates user. Uses XML-RPC protocol
        (https://developer.atlassian.com/server/confluence/confluence-xml-rpc-and-soap-apis/)
        :param username: Username to create
        :param password: Password for user
        :return: user
        """
        proxy = xmlrpc.client.ServerProxy(self.host + "/rpc/xmlrpc")
        token = proxy.confluence2.login(self.user, self.password)

        if not proxy.confluence2.hasUser(token, username):
            user_definition = {
                "email": f"{username}@test.com",
                "fullname": username.capitalize(),
                "name": username,
                "url": self.host + f"/display/~{username}"
            }
            proxy.confluence2.addUser(token, user_definition, password)
            user_definition['password'] = password
            return {
                'user': {
                    'username': user_definition["name"],
                    'email': user_definition["email"]}}
        else:
            raise Exception(
                f"Can't create user {username}: user already exists.")
