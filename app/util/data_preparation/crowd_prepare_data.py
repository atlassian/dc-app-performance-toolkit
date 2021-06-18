import urllib3
import random
import string

from util.conf import CROWD_SETTINGS
from util.api.crowd_clients import CrowdRestClient
from util.project_paths import CROWD_USERS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


USERS = "users"
DEFAULT_USER_PASSWORD = 'password'
DEFAULT_USER_PREFIX = 'performance_'
USER_SEARCH_CQL = f'name={DEFAULT_USER_PREFIX}*'
ERROR_LIMIT = 10

USERS_COUNT = 100000


def generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __get_users(crowd_api, count):
    cur_perf_users = crowd_api.users_search_parallel(cql=USER_SEARCH_CQL, max_results=count)
    if len(cur_perf_users) >= count:
        print(f'{USERS_COUNT} performance test users were found')
        return cur_perf_users
    else:
        raise SystemExit(f'Your Atlassian Crowd instance does not have enough users. '
                         f'Current users count {len(cur_perf_users)} out of {count}.')


def __create_data_set(crowd_api):
    dataset = dict()
    dataset[USERS] = __get_users(crowd_api, USERS_COUNT)

    print(f'Users count: {len(dataset[USERS])}')

    return dataset


def write_test_data_to_files(dataset):

    users = [f"{user},{DEFAULT_USER_PASSWORD}" for user in dataset[USERS]]
    __write_to_file(CROWD_USERS, users)


def __write_to_file(file_path, items):
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")


def main():
    print("Started preparing data")

    url = CROWD_SETTINGS.server_url
    print("Server url: ", url)

    client = CrowdRestClient(url, CROWD_SETTINGS.application_name,
                             CROWD_SETTINGS.application_password, verify=CROWD_SETTINGS.secure)

    dataset = __create_data_set(client)
    write_test_data_to_files(dataset)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
