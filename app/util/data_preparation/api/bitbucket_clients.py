import time
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

    def get_entities(self, entity_name, batch_size, filter_=None, max_results=500):
        print(f'Attempt to fetch [{max_results}] [{entity_name}] from the server')
        entities = []
        entities_to_fetch = max_results
        start_at = 0
        while entities_to_fetch > 0:
            limit = entities_to_fetch if entities_to_fetch < batch_size else batch_size

            api_url = f'{self.host}/rest/api/1.0/{entity_name}?limit={limit}&start={start_at}'
            if filter_:
                api_url += f'&filter={filter_}'

            response = self.get(api_url, f'Could not retrieve entities list')
            returned_entities = response.json()['values']
            entities.extend(returned_entities)
            returned_entities_count = len(returned_entities)
            if returned_entities_count < limit:
                print(f'Stopped fetching [{entity_name}] with filter [{filter_}]'
                      f' since there is no more than [{len(entities)}] on the server')
                break

            start_at = start_at + returned_entities_count
            entities_to_fetch -= limit

        print(f'Totally fetched [{len(entities)}] [{entity_name}] from the server')
        return entities

    def get_non_fork_repos(self, max_results):
        batch_size = 1000
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
                                 filter_=name_filter,
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
        start_time = time.time()
        params = {
            "name": username,
            "password": password if password else username,
            "emailAddress": email if email else f'{username}@localdomain.com',
            "displayName": f'Test-{username}',
            "addToDefaultGroup": True
        }
        api_url = f'{self.host}/rest/api/1.0/admin/users'
        response = self.post(api_url, "Could not create user", params=params)
        print(f'Successfully created user [{username}] in [{(time.time() - start_time)}]')
        return response

    def get_bitbucket_version(self):
        api_url = f'{self.host}/rest/api/1.0/application-properties'
        response = self.get(api_url, 'Could not get Bitbucket properties')
        return response.json()['version']

    def apply_user_permissions(self, name: str, permission: BitbucketUserPermission):
        start_time = time.time()
        params = {
            "name": name,
            "permission": permission.value
        }
        api_url = f'{self.host}/rest/api/1.0/admin/permissions/users'
        response = self.put(api_url, "Could not create user", params=params)
        print(f'Successfully applied user [{name}] permission [{permission.value}] in [{(time.time() - start_time)}]')
        return response
