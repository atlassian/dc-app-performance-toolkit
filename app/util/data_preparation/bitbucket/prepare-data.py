import random
import string

from util.conf import BITBUCKET_SETTINGS
from util.data_preparation.api.bitbucket_clients import BitbucketRestClient
from util.project_paths import BITBUCKET_PROJECTS, BITBUCKET_USERS, BITBUCKET_REPOS, BITBUCKET_PRS

DEFAULT_USER_PREFIX = 'user'
USERS = "users"
PROJECTS = "projects"
REPOS = 'repos'
PULL_REQUESTS = "pull_requests"


def generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __get_users(bitbucket_api):
    perf_user_count = BITBUCKET_SETTINGS.concurrency
    perf_users = bitbucket_api.get_users(username=f'{DEFAULT_USER_PREFIX}', max_results=perf_user_count)
    perf_user_count_to_create = perf_user_count - len(perf_users)
    while perf_user_count_to_create > 0:
        user = bitbucket_api.create_user(username=f'{DEFAULT_USER_PREFIX}-{generate_random_string(5)}')
        perf_users.append(user)
        perf_user_count_to_create = perf_user_count_to_create - 1
    return bitbucket_api.get_users(username=f'{DEFAULT_USER_PREFIX}', max_results=perf_user_count)


def __get_repos(bitbucket_api):
    max_results = 50
    import time
    #start_time = time.time()
    repos = bitbucket_api.get_non_fork_repos(max_results=max_results)
    #print("--- %s seconds ---" % (time.time() - start_time))

    print(f'Repos number to fetch via API is {max_results}')
    return repos


def __get_projects(bitbucket_api):
    max_results = 50
    projects = bitbucket_api.get_projects(max_results=max_results)
    print(f'Projects number to fetch via API is {max_results}')
    return projects


def __get_prs(bitbucket_api, repos):
    repos_prs = []
    for repo in repos:
        repo_prs = [repo['slug'], repo['project']['key']]
        prs = bitbucket_api.get_pull_request(project_key=repo['project']['key'], repo_key=repo['slug'])
        for pr in prs['values']:
            repo_prs.extend([pr['fromRef']['displayId'], pr['toRef']['displayId']])
        repos_prs.append(repo_prs)
    return repos_prs


def __create_data_set(bitbucket_api):
    dataset = dict()
    dataset[USERS] = __get_users(bitbucket_api)
    dataset[PROJECTS] = __get_projects(bitbucket_api)
    dataset[REPOS] = __get_repos(bitbucket_api)
    dataset[PULL_REQUESTS] = __get_prs(bitbucket_api, dataset[REPOS])
    return dataset


def __write_to_file(file_path, items):
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")


def write_test_data_to_files(datasets):
    users = [f"{user['id']},{user['name']},{user['name']}" for user in datasets[USERS]]
    __write_to_file(BITBUCKET_USERS, users)

    projects = [f"{project['key']},{project['id']}" for project in datasets[PROJECTS]]
    __write_to_file(BITBUCKET_PROJECTS, projects)

    repos = [f"{repo['slug']},{repo['project']['key']}" for repo in datasets[REPOS]]
    __write_to_file(BITBUCKET_REPOS, repos)

    prs = [f"{','.join(map(str, pr))}" for pr in datasets[PULL_REQUESTS]]
    __write_to_file(BITBUCKET_PRS, prs)


def main():
    print("Started preparing data")

    url = BITBUCKET_SETTINGS.server_url
    print("Server url: ", url)

    client = BitbucketRestClient(url, BITBUCKET_SETTINGS.admin_login, BITBUCKET_SETTINGS.admin_password)
    dataset = __create_data_set(client)
    write_test_data_to_files(dataset)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
