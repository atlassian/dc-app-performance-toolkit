from enum import Enum

from util.data_preparation.api.abstract_clients import RestClient

BATCH_SIZE_PROJECTS = 100
BATCH_SIZE_USERS = 100
BATCH_SIZE_REPOS = 100


class BitbucketUserPermission(Enum):
    LICENSED_USER = "LICENSED_USER"
    PROJECT_CREATE = "PROJECT_CREATE"
    ADMIN = "ADMIN"
    SYS_ADMIN = "SYS_ADMIN"


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
                # TODO variable max_results is not used, before delete it we should check if there is no bug in the code
                max_results = last_loop_remainder
        return entities

    def get_non_fork_repos(self, max_results):
        batch_size = max_results * 2
        non_fork_repos = []
        start_at = 0
        while len(non_fork_repos) < max_results:
            api_url = f'{self.host}/rest/api/1.0/repos?limit={batch_size}&start={start_at}'
            response = self.get(api_url, f'Could not retrieve entities list')
            for repo in response.json()['values']:
                if 'origin' not in repo and len(non_fork_repos) < max_results:
                    non_fork_repos.append(repo)
            start_at = start_at + batch_size
        return non_fork_repos

    def get_projects(self, max_results=500):
        return self.get_entities(entity_name='projects',
                                 batch_size=BATCH_SIZE_PROJECTS,
                                 max_results=max_results)

    def get_users(self, name_filter, max_results=500):
        return self.get_entities(entity_name='users',
                                 filter=name_filter,
                                 batch_size=BATCH_SIZE_USERS,
                                 max_results=max_results)

    def get_repos(self, max_results=500):
        return self.get_entities(entity_name='repos',
                                 batch_size=BATCH_SIZE_REPOS,
                                 max_results=max_results)

    def get_project_repos(self, project_key):
        api_url = f'{self.host}/rest/api/1.0/projects/{project_key}/repos'
        response = self.get(api_url, f'Could not get repos of project {project_key}')
        return response.json()

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
        response = self.post(api_url, "Could not create user", params=params)
        return response

    def get_bitbucket_version(self):
        api_url = f'{self.host}/rest/api/1.0/application-properties'
        response = self.get(api_url, 'Could not get Bitbucket properties')
        return response.json()['version']

    def change_user_permissions(self, name: str, permission: BitbucketUserPermission):
        params = {
            "name": name,
            "permission": permission.value
        }
        api_url = f'{self.host}/rest/api/1.0/admin/permissions/users'
        response = self.put(api_url, "Could not create user", params=params)
        return response
