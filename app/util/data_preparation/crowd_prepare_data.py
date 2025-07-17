from prepare_data_common import __write_to_file, __warnings_filter
from util.api.crowd_clients import CrowdRestClient
from util.conf import CROWD_SETTINGS
from util.project_paths import CROWD_USERS

__warnings_filter()


USERS = "users"
DEFAULT_USER_PASSWORD = 'password'
DEFAULT_USER_PREFIX = 'performance_'
USER_SEARCH_CQL = f'name={DEFAULT_USER_PREFIX}*'
ERROR_LIMIT = 10

USERS_COUNT = 100000


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


def __check_number_of_custom_app(client):
    try:
        all_apps = client.get_installed_apps()
        apps_with_vendor_defined = [app for app in all_apps if 'vendor' in app]
        non_atlassian_apps = [app for app in apps_with_vendor_defined if 'Atlassian' not in
                              app['vendor']['name'] and app['userInstalled'] == True]
        non_atlassian_apps_names = [app['name'] for app in non_atlassian_apps]
        print(f"Custom application count: {len(non_atlassian_apps)}")
        if non_atlassian_apps:
            print(f'Custom app names:')
            print(*non_atlassian_apps_names, sep='\n')
    except Exception as e:
        print(f'ERROR: Could not get the installed applications. Error: {e}')


def main():
    print("Started preparing data")

    url = CROWD_SETTINGS.server_url
    print("Server url: ", url)

    client = CrowdRestClient(url, CROWD_SETTINGS.application_name,
                             CROWD_SETTINGS.application_password, verify=CROWD_SETTINGS.secure)
    crowd_admin_client = CrowdRestClient(url, CROWD_SETTINGS.admin_login,
                             CROWD_SETTINGS.admin_password, verify=CROWD_SETTINGS.secure)
    dataset = __create_data_set(client)
    write_test_data_to_files(dataset)
    __check_number_of_custom_app(crowd_admin_client)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
