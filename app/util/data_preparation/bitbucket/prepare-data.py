import random
import string

from util.conf import BITBUCKET_SETTINGS
from util.data_preparation.api.bitbucket_clients import BitbucketRestClient
from util.project_paths import BITBUCKET_PROJECTS, BITBUCKET_USERS

DEFAULT_USER_PREFIX = 'user'
USERS = "users"
PROJECTS = "projects"


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


def __get_projects(bitbucket_api):
    repos = bitbucket_api.get_repos()
    projects_dict = {}
    for repo in repos:
        if repo['project']['key'] not in projects_dict:
            projects_dict[repo['project']['key']] = [repo['slug']]
        else:
            projects_dict[repo['project']['key']].append(repo['slug'])
    return projects_dict


def __create_data_set(bitbucket_api):
    dataset = dict()
    dataset[USERS] = __get_users(bitbucket_api)
    dataset[PROJECTS] = __get_projects(bitbucket_api)
    return dataset


def __write_to_file(file_path, items):
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")


def write_test_data_to_files(datasets):
    users = [f"{user['id']},{user['name']},{user['name']}" for user in datasets[USERS]]
    __write_to_file(BITBUCKET_USERS, users)

    projects = [f"{project_key},{','.join(map(str, repo_key))}" for project_key, repo_key in datasets[PROJECTS].items()]
    __write_to_file(BITBUCKET_PROJECTS, projects)


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
