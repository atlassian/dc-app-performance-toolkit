import random
import string
import time

from util.conf import BITBUCKET_SETTINGS
from util.data_preparation.api.bitbucket_clients import BitbucketRestClient, BitbucketUserPermission
from util.project_paths import BITBUCKET_PROJECTS, BITBUCKET_USERS, BITBUCKET_REPOS, BITBUCKET_PRS

DEFAULT_USER_PREFIX = 'dcapt-perf-user'
USERS = "users"
PROJECTS = "projects"
REPOS = 'repos'
PULL_REQUESTS = "pull_requests"

FETCH_LIMIT_REPOS = 50
FETCH_LIMIT_PROJECTS = FETCH_LIMIT_REPOS


def generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __get_users(client: BitbucketRestClient):
    perf_users_desired_number = BITBUCKET_SETTINGS.concurrency
    current_perf_users = client.get_users(f'{DEFAULT_USER_PREFIX}', perf_users_desired_number)
    perf_users_current_number = len(current_perf_users)
    if not (perf_users_current_number < perf_users_desired_number):
        return current_perf_users

    perf_user_count_to_create = perf_users_desired_number - perf_users_current_number
    __create_users(client, perf_user_count_to_create)

    perf_users = client.get_users(f'{DEFAULT_USER_PREFIX}', perf_users_desired_number)
    if len(perf_users) < perf_users_desired_number:
        raise SystemExit(f'Server returned less number of users than expected')

    return perf_users


def __create_users(client: BitbucketRestClient, perf_user_count_to_create):
    while perf_user_count_to_create > 0:
        user_name = f'{DEFAULT_USER_PREFIX}-{generate_random_string(5)}'
        client.create_user(user_name)
        client.apply_user_permissions(user_name, BitbucketUserPermission.ADMIN)
        perf_user_count_to_create = perf_user_count_to_create - 1


def __get_repos(bitbucket_api):
    concurrency = BITBUCKET_SETTINGS.concurrency
    repos = bitbucket_api.get_non_fork_repos(
        FETCH_LIMIT_REPOS if concurrency < FETCH_LIMIT_REPOS else concurrency
    )
    print(f'Repos number to fetch via API is {FETCH_LIMIT_REPOS}')
    repos_len = len(repos)
    if repos_len < concurrency:
        raise SystemExit(f'Required number of repositories based on concurrency was not found'
                         f' Found [{repos_len}] repos, needed at least [{concurrency}]')

    return repos


def __get_projects(bitbucket_api):
    projects = bitbucket_api.get_projects(max_results=FETCH_LIMIT_PROJECTS)
    print(f'Projects number to fetch via API is {FETCH_LIMIT_PROJECTS}')
    return projects


def __get_prs(bitbucket_api):
    concurrency = BITBUCKET_SETTINGS.concurrency
    repos_prs = []
    REPOS_TO_FETCH = 1000
    start_time = time.time()
    repos = bitbucket_api.get_non_fork_repos(REPOS_TO_FETCH)
    for repo in repos:
        if len(repos_prs) <= concurrency:
            prs = bitbucket_api.get_pull_request(project_key=repo['project']['key'], repo_key=repo['slug'])
            for pr in prs['values']:
                repos_prs.append([repo['slug'], repo['project']['key'], pr['id'], pr['fromRef']['displayId'], pr['toRef']['displayId']])
    if len(repos_prs) < concurrency:
        raise SystemExit(f'Repositories from list {[repo["project"]["key"] - repo["slug"] for repo in repos]} '
                         f'do not contain {concurrency} pull requests')
    print(f"Successfully fetched pull requests in  [{(time.time() - start_time)}]")
    return repos_prs


def __create_data_set(bitbucket_api):
    dataset = dict()
    dataset[USERS] = __get_users(bitbucket_api)
    dataset[PROJECTS] = __get_projects(bitbucket_api)
    dataset[REPOS] = __get_repos(bitbucket_api)
    dataset[PULL_REQUESTS] = __get_prs(bitbucket_api)
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
