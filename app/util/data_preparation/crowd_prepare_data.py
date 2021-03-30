import urllib3
import random
import string

from util.conf import CROWD_SETTINGS
from util.api.crowd_clients import CrowdRestClient
from util.project_paths import CROWD_USERS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


USERS = "users"
DEFAULT_USER_PASSWORD = 'password'
DEFAULT_USER_PREFIX = 'performance'
USER_SEARCH_CQL = f'name={DEFAULT_USER_PREFIX}*'
ERROR_LIMIT = 10


def generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __get_users(crowd_api, count):
    errors_count = 0
    cur_perf_users = crowd_api.users_search_parallel(cql=USER_SEARCH_CQL, max_results=count)
    if len(cur_perf_users) >= count:
        return cur_perf_users

    # while len(cur_perf_users) < count:
    #     if errors_count >= ERROR_LIMIT:
    #         raise Exception(f'Maximum error limit reached {errors_count}/{ERROR_LIMIT}. '
    #                         f'Please check the errors in bzt.log')
    #     username = f"{DEFAULT_USER_PREFIX}{generate_random_string(10)}"
    #     try:
    #
    #         user = rpc_api.create_user(username=username, password=DEFAULT_USER_PASSWORD)
    #
    #         print(f"User {user['user']['username']} is created, number of users to create is "
    #               f"{count - len(cur_perf_users)}")
    #         cur_perf_users.append(user)
    #     # To avoid rate limit error from server. Execution should not be stopped after catch error from server.
    #     except Exception as error:
    #         print(f"Warning: Create confluence user error: {error}. Retry limits {errors_count}/{ERROR_LIMIT}")
    #         errors_count = errors_count + 1
    # print('All performance test users were successfully created')
    return cur_perf_users


def __create_data_set(crowd_api):
    dataset = dict()
    dataset[USERS] = __get_users(crowd_api, CROWD_SETTINGS.concurrency)

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

