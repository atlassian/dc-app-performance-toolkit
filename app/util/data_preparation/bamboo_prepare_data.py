import urllib3

from prepare_data_common import __generate_random_string, __write_to_file
from util.api.bamboo_clients import BambooClient
from util.conf import BAMBOO_SETTINGS
from util.project_paths import BAMBOO_BUILD_PLANS, BAMBOO_USERS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BUILD_PLANS = 'plans'
USERS = 'users'
PROJECTS = 'projects'
DEFAULT_PASSWORD = 'password'


def get_users(client, users_count):
    existing_users = client.get_users(users_count)
    users_to_generate = 0
    users = []
    if len(existing_users) < users_count:
        users_to_generate = users_count - len(existing_users)
    users.extend(existing_users)
    if users_to_generate:
        for i in range(0, users_to_generate):
            username = f'performance_user_{__generate_random_string(5)}'
            password = DEFAULT_PASSWORD
            generated_user = client.create_user(name=username, password=password)
            users.append(generated_user)
    return users


def generate_project_name_keys_dict(client):
    projects_name_key_dict = {}
    projects = client.get_projects()
    for project in projects:
        projects_name_key_dict[project['name']] = project['key']
    return projects_name_key_dict


def __create_dataset(client):
    dataset = dict()
    dataset[BUILD_PLANS] = client.get_build_plans(max_result=2000)
    dataset[PROJECTS] = generate_project_name_keys_dict(client)
    dataset[USERS] = get_users(client, BAMBOO_SETTINGS.concurrency)

    return dataset


def write_test_data_to_files(dataset):
    build_plans = [f"{dataset[PROJECTS][build_plan['searchEntity']['projectName']]},{build_plan['id']}" for
                   build_plan in dataset[BUILD_PLANS]]
    __write_to_file(BAMBOO_BUILD_PLANS, build_plans)
    users = [f"{user['name']},{DEFAULT_PASSWORD}" for user in dataset[USERS] if user['name'] != 'admin']
    __write_to_file(BAMBOO_USERS, users)


def main():
    print("Started preparing data")

    url = BAMBOO_SETTINGS.server_url
    print("Server url: ", url)

    client = BambooClient(url, BAMBOO_SETTINGS.admin_login, BAMBOO_SETTINGS.admin_password,
                          verify=BAMBOO_SETTINGS.secure)

    dataset = __create_dataset(client)
    write_test_data_to_files(dataset)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
