import random
import xmlrpc.client
from pathlib import Path

import requests

# TODO extract paths to project_paths
with open(Path(__file__).parents[2] / "confluence" / "resources" / "names.txt") as file:
    __NAMES = [line.rstrip('\n') for line in file]


def random_names(number=2):
    return [random.choice(__NAMES) for _ in range(number)]


# TODO use OOP approach for ApiJira and ApiConfluence
class ApiConfluence:

    def __init__(self, host, user, password, api_session=None, timeout=30):
        self.host = host
        self.requests_timeout = timeout
        self.user = user
        self.password = password
        if api_session is None:
            self.api_session = requests.Session()
        else:
            self.api_session = api_session
        self._base_auth = user, password

    @property
    def base_auth(self):
        return self._base_auth

    @base_auth.setter
    def base_auth(self, auth):
        self._base_auth = auth

    def get_content(self, startAt=0, maxResults=100, type="page", expand="space"):
        """
        Returns all content. This only includes pages that the user has permission to view.
        :param startAt: The starting index of the returned boards. Base index: 0.
        :param maxResults: The maximum number of boards to return per page. Default: 50.
        :param type: Filters results to boards of the specified type. Valid values: page, blogpost
        :param expand: Responds with additional values. Valid values: space,history,body.view,metadata.label
        :return: Returns the requested content, at the specified page of the results.
        """
        fetched_records_per_call = 200
        loop_count = maxResults // fetched_records_per_call + 1
        content = list()
        last_loop_remainder = maxResults % fetched_records_per_call

        while loop_count > 0:
            api_url = self.host + f'/rest/api/content?&start={startAt}&limit={maxResults}&type={type}&expand={expand}'
            r = self.api_session.get(api_url, auth=self.base_auth, verify=False, timeout=self.requests_timeout)
            assert r.ok, f"Could not retrieve content: {r.status_code} {r.text}"
            content.extend(r.json()['results'])
            loop_count = loop_count - 1
            startAt = startAt + len(r.json()['results'])
            if loop_count == 1:
                maxResults = last_loop_remainder
            assert len(content) > 0, f"Content with type {type} is empty"
        return content

    def create_users(self, prefix="performance", count=100):
        """
        Creates users. Uses XML-RPC protocol
        (https://developer.atlassian.com/server/confluence/confluence-xml-rpc-and-soap-apis/)
        :param prefix: The prefix of all usernames to be created.
        :param count: The number of users to create, if not already exist.
        :return: Returns a list of tuples, containing usernames and passwords.
        """
        proxy = xmlrpc.client.ServerProxy(self.host + "/rpc/xmlrpc")
        token = proxy.confluence2.login(self.user, self.password)
        users = list()

        for index in range(count):
            username = f"{prefix}{index}"

            if not proxy.confluence2.hasUser(token, username):
                names = random_names(2)
                user_definition = {"email": f"{username}@test.com",
                                   "fullname": f"{names[0]} {names[1]}",
                                   "name": username,
                                   "url": self.host + f"/display/~{prefix}"
                                   }
                proxy.confluence2.addUser(token, user_definition, self.password)
            users.append((username, self.password))
        return users
