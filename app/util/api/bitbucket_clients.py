import time
from enum import Enum

from util.api.abstract_clients import RestClient, LOGIN_POST_HEADERS
from lxml import html

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
        batch_size = None
        non_fork_repos = []
        start_at = 0
        while len(non_fork_repos) < max_results:
            api_url = f'{self.host}/rest/api/1.0/repos?limit={batch_size if batch_size else 1000}&start={start_at}'
            response = self.get(api_url, f'Could not retrieve entities list')
            if not batch_size:
                batch_size = response.json()['limit']
            repos = response.json()['values']
            for repo in repos:
                if 'origin' not in repo:
                    non_fork_repos.append(repo)
                    if len(non_fork_repos) == max_results:
                        return non_fork_repos
            if response.json()['isLastPage']:
                break
            start_at = response.json()['nextPageStart']
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
        response = self.get(api_url, 'Could not retrieve pull requests list')
        return response.json()

    def check_pull_request_has_conflicts(self, project_key, repo_key, pr_id):
        api_url = f'{self.host}/rest/api/1.0/projects/{project_key}/repos/{repo_key}/pull-requests/{pr_id}/merge'
        response = self.get(api_url, f'Could not get pull request merge status')
        return response.json()['conflicted']

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

    def get_bitbucket_cluster_page(self):
        session = self._session
        url = f"{self.host}/admin/clustering"
        body = {
            '_atl_remember_me': 'on',
            'j_password': self.password,
            'j_username': self.user,
            'next': '/admin/clustering',
            'queryString': 'next=/admin/clustering',
            'submit': 'Log in'
        }
        headers = LOGIN_POST_HEADERS
        headers['Origin'] = self.host
        r = session.post(url, data=body, headers=headers)
        cluster_html = r.content.decode("utf-8")
        return cluster_html

    def get_bitbucket_nodes_count(self):
        cluster_page = self.get_bitbucket_cluster_page()
        nodes_count = cluster_page.count('class="cluster-node-id" headers="cluster-node-id"')
        if nodes_count == 0:
            nodes_count = "Server"
        return nodes_count

    def get_bitbucket_system_page(self):
        session = self._session
        url = f"{self.host}/j_atl_security_check"
        body = {'j_username': self.user, 'j_password': self.password, '_atl_remember_me': 'on',
                'next': f"{self.host}/plugins/servlet/troubleshooting/view/system-info/view",
                'submit': 'Log in'}
        headers = LOGIN_POST_HEADERS
        headers['Origin'] = self.host
        session.post(url, data=body, headers=headers)
        response = session.get(f"{self.host}/plugins/servlet/troubleshooting/view/system-info/view")
        return response

    def get_bitbucket_repo_count(self):
        repos_count = None
        page = self.get_bitbucket_system_page()
        tree = html.fromstring(page.content)
        try:
            repos_count = tree.xpath('//*[@id="content-bitbucket.atst.repositories-0"]/div[1]/span/text()')[0]
        except Exception as error:
            print(f"Warning: Could not parse number of Bitbucket repositories: {error}")
        return repos_count

    def get_available_processors(self):
        processors = None
        page = self.get_bitbucket_system_page()
        tree = html.fromstring(page.content)
        try:
            processors = tree.xpath('//*[@id="content-stp.properties.os-0"]/div[4]/span/text()')[0]
        except Exception as error:
            print(f"Warning: Could not parse number of Bitbucket available processors: {error}")
        return processors

    def get_locale(self):
        language = None
        page = self.get(f'{self.host}/dashboard', "Could not get page content.", headers=LOGIN_POST_HEADERS)
        tree = html.fromstring(page.content)
        try:
            language = tree.xpath('//html/@lang')[0]
        except Exception as error:
            print(f"Warning: Could not get user locale: {error}")
        return language

    def get_user_global_permissions(self, user=''):
        api_url = f'{self.host}/rest/api/1.0/admin/permissions/users?filter={user}'
        response = self.get(api_url, "Could not get user global permissions")
        return response.json()

    def get_deployment_type(self):
        html_pattern = 'com.atlassian.dcapt.deployment=terraform'
        bitbucket_system_page = self.get_bitbucket_system_page().content.decode("utf-8")
        if bitbucket_system_page.count(html_pattern):
            return 'terraform'
        return 'other'
