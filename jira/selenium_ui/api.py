import json
import requests
import yaml
from pathlib import Path


def admin_credentials():
    with open(Path(__file__).parents[1] / "jira.yml", 'r') as file:
        jira_yaml = yaml.load(file, Loader=yaml.FullLoader)
        return jira_yaml['settings']['env']['admin_login'], jira_yaml['settings']['env']['admin_password']


USER, PASSWORD = admin_credentials()


class ApiJira(object):

    def __init__(self, host, api_session=None, timeout=30):
        self.host = host
        self.requests_timeout = timeout
        if api_session is None:
            self.api_session = requests.Session()
        else:
            self.api_session = api_session

    @property
    def base_auth(self):
        return USER, PASSWORD

    def get_boards(self, startAt=0, maxResults=100, type=None, name=None, projectKeyOrID=None):
        """
        Returns all boards. This only includes boards that the user has permission to view.
        :param startAt: The starting index of the returned boards. Base index: 0.
        :param maxResults: The maximum number of boards to return per page. Default: 100.
        :param type: Filters results to boards of the specified type. Valid values: scrum, kanban.
        :param name: Filters results to boards that match or partially match the specified name.
        :param projectKeyOrID: Filters results to boards that are relevant to a project.
        Relevance meaning that the jql filter defined in board contains a reference to a project.
        :return: Returns the requested boards, at the specified page of the results.
        """
        fetched_records_per_call = 1000
        loop_count = maxResults // fetched_records_per_call + 1
        last_loop_remainder = maxResults % fetched_records_per_call

        boards_list = list()
        maxResults = fetched_records_per_call

        while loop_count > 0:
            api_url = f"{self.host}/rest/agile/1.0/board?startAt={startAt}&maxResults={maxResults}"

            if type:
                api_url = api_url + f"&type={type}"
            if name:
                api_url = api_url + f"&name={name}"
            if projectKeyOrID:
                api_url = api_url + f"&projectKeyOrID={projectKeyOrID}"

            r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
            assert r.ok, f"Could not retrieve boards: {r.status_code} {r.text}"

            boards_list.extend(r.json()['values'])
            loop_count = loop_count - 1
            startAt = startAt + len(r.json()['values'])
            if loop_count == 1:
                maxResults = last_loop_remainder

        return boards_list

    def get_users(self, username='.', startAt=0, maxResults=1000, includeActive=True, includeInactive=False):
        """
        Returns a list of users that match the search string. This resource cannot be accessed anonymously.
        :param username: A query string used to search username, name or e-mail address. "." - search for all users.
        :param startAt: the index of the first user to return (0-based).
        :param maxResults: the maximum number of users to return (defaults to 50).
        The maximum allowed value is 1000.
        If you specify a value that is higher than this number, your search results will be truncated.
        :param includeActive: If true, then active users are included in the results (default true)
        :param includeInactive: If true, then inactive users are included in the results (default false)
        :return: Returns the requested users
        """

        fetched_records_per_call = 1000
        loop_count = maxResults // fetched_records_per_call + 1
        last_loop_remainder = maxResults % fetched_records_per_call

        users_list = list()
        maxResults = fetched_records_per_call

        while loop_count > 0:

            api_url = f'{self.host}/rest/api/2/user/search?username={username}&startAt={startAt}' \
                  f'&maxResults={maxResults}&includeActive={includeActive}&includeInactive={includeInactive}'

            r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
            assert r.ok, f"Could not retrieve users: {r.status_code} {r.text}"
            users_list.extend(r.json())
            loop_count = loop_count - 1
            startAt = startAt + len(r.json())
            if loop_count == 1:
                maxResults = last_loop_remainder

        return users_list

    def issues_search(self, jql='order by key', startAt=0, maxResults=1000, validateQuery=True, fields='id'):
        """
        Searches for issues using JQL.
        :param jql: a JQL query string
        :param startAt: the index of the first issue to return (0-based)
        :param maxResults: the maximum number of issues to return (defaults to 50).
        :param validateQuery: whether to validate the JQL query
        :param fields: the list of fields to return for each issue. By default, all navigable fields are returned.
        *all - include all fields
        *navigable - include just navigable fields
        summary,comment - include just the summary and comments
        -description - include navigable fields except the description (the default is *navigable for search)
        *all,-comment - include everything except comments
        :return: Returns the requested issues
        """
        fetched_records_per_call = 1000
        loop_count = maxResults // fetched_records_per_call + 1
        issues = list()
        last_loop_remainder = maxResults % fetched_records_per_call

        while loop_count > 0:
            api_url = f'{self.host}/rest/api/2/search?jql={jql}&startAt={startAt}&maxResults={maxResults}' \
                f'&validateQuery={validateQuery}&fields={fields}'
            r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
            assert r.ok, f"Could not retrieve users: {r.status_code} {r.text}"
            issues.extend(r.json()['issues'])
            loop_count = loop_count - 1
            startAt = startAt + len(r.json()['issues'])
            if loop_count == 1:
                maxResults = last_loop_remainder

        return issues

    def get_app_info(self, app_key):
        api_url = f'{self.host}/rest/plugins/1.0/{app_key}-key'
        r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
        assert r.ok, f"Could not get application info with application key {app_key}, code: {r.status_code}"
        return r.json()

    def update_app(self, app_key, payload):
        api_url =  f'{self.host}/rest/plugins/1.0/{app_key}-key'
        headers = {"content-type": "application/vnd.atl.plugins.plugin+json"}
        r = self.api_session.put(api_url, auth=self.base_auth, headers=headers, verify=False, json=payload)
        assert r.ok, f"Could not update application {app_key}"

    def create_user(self, displayname=None, email=None, name='', password=''):
        """
        Creates a user. This resource is retained for legacy compatibility.
        As soon as a more suitable alternative is available this resource will be deprecated.
        :param name: The username for the user. This property is deprecated because of privacy changes.
        :param password: A password for the user. If a password is not set, a random password is generated.
        :param emailAddress: tThe email address for the user. Required.
        :param displayName: The display name for the user. Required.
        :param notification: Sends the user an email confirmation that they have been added to Jira. Default is false.
        :return: Returns the created user.
        """
        if not email:
            email = name+'@localdomain.com'
        if not displayname:
            displayname = name
        payload = json.dumps({
            "name": name,
            "password": password,
            "emailAddress": email,
            "displayName": displayname
        })
        api_url = self.host + "/rest/api/2/user"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        r = self.api_session.post(api_url, payload, auth=self.base_auth, headers=headers)
        assert r.ok, f"Could not create user: {r.status_code} {r.text}"
        return r.json()
