from util.data_preparation.api.abstract_clients import RestClient

BATCH_SIZE_PROJECTS = 500
BATCH_SIZE_USERS = 500


class BitbucketRestClient(RestClient):

    def get_entities(self, entity_name, batch_size, filter=None, max_results=500):
        entities = []
        loop_count = max_results // batch_size
        if loop_count == 0:
            loop_count = 1
        last_loop_remainder = max_results % batch_size
        start_at = 0
        while loop_count > 0:
            if not filter:
                api_url = f'{self.host}/rest/api/1.0/{entity_name}?limit={batch_size}&start={start_at}'
            else:
                api_url = f'{self.host}/rest/api/1.0/{entity_name}?limit={batch_size}&start={start_at}&filter={filter}'
            response = self.get(api_url, f'Could not retrieve entities list')
            entities.extend(response.json()['values'])
            start_at = start_at + len(response.json()['values'])
            loop_count -= 1
            if loop_count == 1:
                max_results = last_loop_remainder
        return entities

    def get_projects(self, max_results=500):
        return self.get_entities(entity_name='projects',
                                 batch_size=BATCH_SIZE_PROJECTS,
                                 max_results=max_results)

    def get_users(self, username, max_results=500):
        return self.get_entities(entity_name=f'users',
                                 filter=username,
                                 batch_size=BATCH_SIZE_USERS,
                                 max_results=max_results)

    def get_repos(self, max_results=500):
        return self.get_entities(entity_name='repos',
                                 batch_size=BATCH_SIZE_PROJECTS,
                                 max_results=max_results)

    def get_pull_request(self, project_key, repo_key):
        api_url = f'{self.host}/rest/api/1.0/projects/{project_key}/repos/{repo_key}/pull-requests'
        response = self.get(api_url, f'Could not retrieve pull requests list')
        return response.json()

    def create_user(self, username, password=None, email=None):
        if not password:
            password = username
        if not email:
            email = f'{username}@localdomain.com'

        params = {
            "name": username,
            "password": password,
            "emailAddress": email,
            "displayName": f'Test-{username}',
            "addToDefaultGroup": True
        }
        api_url = f'{self.host}/rest/api/1.0/admin/users'
        response = self.post(api_url, params, error_msg="Could not create user", to_json=False)
        #return response.json()
