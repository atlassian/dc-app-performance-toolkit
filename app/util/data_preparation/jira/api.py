import json

import requests

BATCH_SIZE_BOARDS = 1000
BATCH_SIZE_USERS = 1000
BATCH_SIZE_ISSUES = 1000


class ApiJira(object):

    def __init__(self, host, user, password, api_session=None, timeout=30):
        self.host = host
        self.requests_timeout = timeout
        self.user = user
        self.password = password
        self.api_session = requests.Session() if api_session is None else api_session

    @property
    def base_auth(self):
        return self.user, self.password

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
        max_results = BATCH_SIZE_BOARDS

        while loop_count > 0:
            api_url = f"{self.host}/rest/agile/1.0/board?startAt={start_at}&maxResults={max_results}"

            if board_type:
                api_url = api_url + f"&type={board_type}"
            if name:
                api_url = api_url + f"&name={name}"
            if project_key_or_id:
                api_url = api_url + f"&projectKeyOrID={project_key_or_id}"

            r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
            assert r.ok, f"Could not retrieve boards: {r.status_code} {r.text}"

            boards_list.extend(r.json()['values'])
            loop_count = loop_count - 1
            start_at = start_at + len(r.json()['values'])
            if loop_count == 1:
                max_results = last_loop_remainder

        return boards_list

    def get_users(self, username='.', start_at=0, max_results=1000, include_active=True, include_inactive=False):
        """
        Returns a list of users that match the search string. This resource cannot be accessed anonymously.
        :param username: A query string used to search username, name or e-mail address. "." - search for all users.
        :param start_at: the index of the first user to return (0-based).
        :param max_results: the maximum number of users to return (defaults to 50).
        The maximum allowed value is 1000.
        If you specify a value that is higher than this number, your search results will be truncated.
        :param include_active: If true, then active users are included in the results (default true)
        :param include_inactive: If true, then inactive users are included in the results (default false)
        :return: Returns the requested users
        """

        loop_count = max_results // BATCH_SIZE_USERS + 1
        last_loop_remainder = max_results % BATCH_SIZE_USERS

        users_list = list()
        max_results = BATCH_SIZE_USERS

        while loop_count > 0:

            api_url = f'{self.host}/rest/api/2/user/search?username={username}&startAt={start_at}' \
                      f'&maxResults={max_results}&includeActive={include_active}&includeInactive={include_inactive}'

            r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
            assert r.ok, f"Could not retrieve users: {r.status_code} {r.text}"
            users_list.extend(r.json())
            loop_count = loop_count - 1
            start_at = start_at + len(r.json())
            if loop_count == 1:
                max_results = last_loop_remainder

        return users_list

    def issues_search(self, jql='order by key', start_at=0, max_results=1000, validate_query=True, fields='id'):
        """
        Searches for issues using JQL.
        :param jql: a JQL query string
        :param start_at: the index of the first issue to return (0-based)
        :param max_results: the maximum number of issues to return (defaults to 50).
        :param validate_query: whether to validate the JQL query
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

        while loop_count > 0:
            api_url = f'{self.host}/rest/api/2/search?jql={jql}&startAt={start_at}&maxResults={max_results}' \
                      f'&validateQuery={validate_query}&fields={fields}'
            r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
            assert r.ok, f"Could not retrieve issues: {r.status_code} {r.text}"
            current_issues = r.json()['issues']
            issues.extend(current_issues)
            start_at += len(current_issues)
            loop_count -= 1
            if loop_count == 1:
                max_results = last_loop_remainder

        return issues

    def get_app_info(self, app_key):
        api_url = f'{self.host}/rest/plugins/1.0/{app_key}-key'
        r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
        assert r.ok, f"Could not get application info with application key {app_key}, code: {r.status_code}"
        return r.json()

    def update_app(self, app_key, payload):
        api_url = f'{self.host}/rest/plugins/1.0/{app_key}-key'
        headers = {"content-type": "application/vnd.atl.plugins.plugin+json"}
        r = self.api_session.put(api_url, auth=self.base_auth, headers=headers, verify=False, json=payload)
        assert r.ok, f"Could not update application {app_key}"

    def create_user(self, display_name=None, email=None, name='', password=''):
        """
        Creates a user. This resource is retained for legacy compatibility.
        As soon as a more suitable alternative is available this resource will be deprecated.
        :param name: The username for the user. This property is deprecated because of privacy changes.
        :param password: A password for the user. If a password is not set, a random password is generated.
        :param email: tThe email address for the user. Required.
        :param display_name: The display name for the user. Required.
        :return: Returns the created user.
        """
        if not email:
            email = name + '@localdomain.com'
        if not display_name:
            display_name = name
        payload = json.dumps({
            "name": name,
            "password": password,
            "emailAddress": email,
            "displayName": display_name
        })
        api_url = self.host + "/rest/api/2/user"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        r = self.api_session.post(api_url, payload, auth=self.base_auth, headers=headers)
        assert r.ok, f"Could not create user: {r.status_code} {r.text}"
        return r.json()

    def get_all_projects(self):
        """
        :return: Returns the projects list of all project types - all categories
        """
        api_url = f'{self.host}/rest/api/2/project'
        r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
        assert r.ok, 'Could not get the list of projects'

        return r.json()
