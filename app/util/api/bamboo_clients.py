from util.api.abstract_clients import RestClient

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

            content.extend(request.json()['searchResults'])

            loop_count -= 1
            if loop_count == 1:
                max_result = last_loop_remainder

            start += len(request.json()['searchResults'])

        return content

    def get_users(self, limit):
        """
        Retrieve a page of users. The authenticated user must have restricted
        administrative permission or higher to use this resource.
        :param start: The starting index of the returned boards. Base index: 0.
        :param limit: The maximum number of boards to return per page. Default: 50.
        """
        request = self.get(f'{self.host}/rest/api/latest/admin/users?limit={limit}',
                           error_msg="Can not retrieve users")
        content = request.json()
        return content['results']

    def create_user(self, username, password):
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
        payload = {"name": username,
                   "fullName": username,
                   "email": f'{username}@example.com',
                   "password": password,
                   "passwordConfirm": password}
        request = self.post(api_url, body = payload, error_msg="Could not create user")
        if request.ok:
            return {'name': username}
        else:
            raise Exception(f'Can not create user')
