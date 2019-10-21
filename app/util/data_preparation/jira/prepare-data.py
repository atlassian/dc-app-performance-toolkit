import random
import string
import sys

import yaml

from util.data_preparation.jira.api import ApiJira
from util.project_paths import JIRA_YML, JIRA_DATASET_JQLS, JIRA_DATASET_SCRUM_BOARDS, JIRA_DATASET_KANBAN_BOARDS, \
    JIRA_DATASET_USERS, JIRA_DATASET_ISSUES, JIRA_DATASET_PROJECT_KEYS

KANBAN_BOARDS = "kanban_boards"
SCRUM_BOARDS = "scrum_boards"
USERS = "users"
ISSUES = "issues"
JQLS = "jqls"
PROJECT_KEYS = "project_keys"

DEFAULT_USER_PASSWORD = 'password'
DEFAULT_USER_PREFIX = 'performance_'


def __generate_jqls(max_length=3, count=100):
    # Generate jqls like "abc*"
    return ['text ~ "{}*" order by key'.format(
        ''.join(random.choices(string.ascii_lowercase, k=max_length))) for _ in range(count)]


def get_perf_users_count():
    with JIRA_YML.open(mode='r') as file:
        jira_yaml = yaml.load(file, Loader=yaml.FullLoader)
        users_count = jira_yaml['settings']['env']['concurrency']
        return users_count


# https://jira.atlassian.com/browse/JRASERVER-65089 User search startAt parameter is not working
performance_users_count = 1000 if get_perf_users_count() > 1000 else get_perf_users_count()


def generate_perf_users(cur_perf_user, api):
    config_perf_users_count = get_perf_users_count()
    if len(cur_perf_user) >= config_perf_users_count:
        return cur_perf_user[:config_perf_users_count]
    else:
        while len(cur_perf_user) < config_perf_users_count:
            username = f"{DEFAULT_USER_PREFIX}{generate_random_string(10)}"
            try:
                user = api.create_user(name=username, password=DEFAULT_USER_PASSWORD)
                print(f"User {user['name']} is created, number of users to create is "
                      f"{config_perf_users_count - len(cur_perf_user)}")
                cur_perf_user.append(user)
            # To avoid rate limit error from server. Execution should not be stopped after catch error from server.
            except Exception as error:
                print(error)
        print('All performance test users were successfully created')
        return cur_perf_user


def generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def write_test_data_to_files(datasets):
    __write_to_file(JIRA_DATASET_JQLS, datasets[JQLS])

    scrum_boards = [board['id'] for board in datasets[SCRUM_BOARDS]]
    __write_to_file(JIRA_DATASET_SCRUM_BOARDS, scrum_boards)

    kanban_boards = [board['id'] for board in datasets[KANBAN_BOARDS]]
    __write_to_file(JIRA_DATASET_KANBAN_BOARDS, kanban_boards)

    users = [f"{user['name']},{DEFAULT_USER_PASSWORD}" for user in datasets[USERS]]
    __write_to_file(JIRA_DATASET_USERS, users)

    issues = [f"{issue['key']},{issue['id']},{issue['key'].split('-')[0]}" for issue in datasets[ISSUES]]
    __write_to_file(JIRA_DATASET_ISSUES, issues)

    keys = datasets[PROJECT_KEYS]
    __write_to_file(JIRA_DATASET_PROJECT_KEYS, keys)


def __write_to_file(file_path, items):
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")


def __create_data_set(jira_api):
    dataset = dict()
    dataset[USERS] = __get_users(jira_api)
    software_project_keys = __get_software_project_keys(jira_api)
    dataset[PROJECT_KEYS] = software_project_keys
    dataset[ISSUES] = __get_issues(jira_api, software_project_keys)
    dataset[SCRUM_BOARDS] = __get_boards(jira_api, 'scrum')
    dataset[KANBAN_BOARDS] = __get_boards(jira_api, 'kanban')
    dataset[JQLS] = __generate_jqls(count=150)

    return dataset


def __get_issues(jira_api, software_project_keys):
    issues = jira_api.issues_search(
        jql=f"project in ({','.join(software_project_keys)}) AND status != Closed order by key", max_results=8000
    )
    if not issues:
        raise SystemExit("There is no issues in Jira")

    return issues


def __get_boards(jira_api, board_type):
    boards = jira_api.get_boards(board_type=board_type, max_results=250)
    if not boards:
        raise SystemExit(f"There is no {board_type} board in Jira")

    return boards


def __get_users(jira_api):
    perf_users = jira_api.get_users(username=DEFAULT_USER_PREFIX, max_results=performance_users_count)
    users = generate_perf_users(api=jira_api, cur_perf_user=perf_users)
    if not users:
        raise SystemExit("There is no users in Jira")

    return users


def __get_software_project_keys(jira_api):
    all_projects = jira_api.get_all_projects()
    software_project_keys = [project['key'] for project in all_projects if 'software' == project.get('projectTypeKey')]
    if not software_project_keys:
        raise SystemExit("There is no software project in Jira")

    return software_project_keys


def main():
    print("Started preparing data")

    # TODO consider getting server url from jira.yml see get_perf_users_count()
    url = sys.argv[1]
    print("Server url: ", url)

    # TODO consider reading jira.yml only once
    with JIRA_YML.open(mode='r') as file:
        jira_yaml = yaml.load(file, Loader=yaml.FullLoader)
        user, password = jira_yaml['settings']['env']['admin_login'], jira_yaml['settings']['env']['admin_password']

    jira_api = ApiJira(url, user, password)
    dataset = __create_data_set(jira_api)
    write_test_data_to_files(dataset)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
