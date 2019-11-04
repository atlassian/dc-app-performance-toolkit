import random
import xmlrpc.client
from pathlib import Path

from util.data_preparation.api.abstract_clients import RestClient, Client


class ConfluenceRestClient(RestClient):

    def get_content(self, start_at=0, max_results=100, board_type="page", expand="space"):
        """
        Returns all content. This only includes pages that the user has permission to view.
        :param start_at: The starting index of the returned boards. Base index: 0.
        :param max_results: The maximum number of boards to return per page. Default: 50.
        :param board_type: Filters results to boards of the specified type. Valid values: page, blogpost
        :param expand: Responds with additional values. Valid values: space,history,body.view,metadata.label
        :return: Returns the requested content, at the specified page of the results.
        """
        fetched_records_per_call = 200
        loop_count = max_results // fetched_records_per_call + 1
        content = list()
        last_loop_remainder = max_results % fetched_records_per_call

        while loop_count > 0:
            api_url = (
                    self.host + f'/rest/api/content?&start={start_at}' +
                    f'&limit={max_results}' +
                    f'&type={board_type}' +
                    f'&expand={expand}'
            )
            request = self.get(api_url, "Could not retrieve content")

            content.extend(request.json()['results'])
            if len(content) < 0:
                raise Exception(f"Content with type {board_type} is empty")

            loop_count -= 1
            if loop_count == 1:
                max_results = last_loop_remainder

            start_at += len(request.json()['results'])

        return content


class ConfluenceRpcClient(Client):
    __user_names: list = None

    @property
    def user_names(self):
        if not self.__user_names:
            self.__user_names = self.__read_names()

        return self.__user_names

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
                names = self.__get_random_names(2)
                user_definition = {
                    "email": f"{username}@test.com",
                    "fullname": f"{names[0]} {names[1]}",
                    "name": username,
                    "url": self.host + f"/display/~{prefix}"
                }
                proxy.confluence2.addUser(token, user_definition, self.password)

            users.append((username, self.password))

        return users

    def __get_random_names(self, number=2):
        return [random.choice(self.user_names) for _ in range(number)]

    @staticmethod
    def __read_names():
        # TODO extract paths to project_paths
        with open(Path(__file__).parents[2] / "confluence" / "resources" / "names.txt") as file:
            return [line.rstrip('\n') for line in file]
