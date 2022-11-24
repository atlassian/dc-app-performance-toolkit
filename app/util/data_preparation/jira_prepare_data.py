import random
import string

from prepare_data_common import __generate_random_string, __write_to_file, __warnings_filter
from util.api.jira_clients import JiraRestClient
from util.conf import JIRA_SETTINGS
from util.project_paths import JIRA_DATASET_JQLS, JIRA_DATASET_SCRUM_BOARDS, JIRA_DATASET_KANBAN_BOARDS, \
    JIRA_DATASET_USERS, JIRA_DATASET_ISSUES, JIRA_DATASET_PROJECTS, JIRA_DATASET_CUSTOM_ISSUES

__warnings_filter()

KANBAN_BOARDS = "kanban_boards"
SCRUM_BOARDS = "scrum_boards"
USERS = "users"
ISSUES = "issues"
JQLS = "jqls"
PROJECTS = "projects"
CUSTOM_ISSUES = "custom_issues"

DEFAULT_USER_PASSWORD = 'password'
DEFAULT_USER_PREFIX = 'performance_'
ERROR_LIMIT = 10

ENGLISH = 'en_US'


def __generate_jqls(max_length=3, count=100):
    # Generate jqls like "abc*"
    return ['text ~ "{}*" order by key'.format(
        ''.join(random.choices(string.ascii_lowercase, k=max_length))) for _ in range(count)]


# https://jira.atlassian.com/browse/JRASERVER-65089 User search startAt parameter is not working
performance_users_count = 1000 if JIRA_SETTINGS.concurrency > 1000 else JIRA_SETTINGS.concurrency


def generate_perf_users(cur_perf_user, api):
    errors_count = 0
    config_perf_users_count = JIRA_SETTINGS.concurrency
    if len(cur_perf_user) >= config_perf_users_count:
        return cur_perf_user[:config_perf_users_count]
    else:
        while len(cur_perf_user) < config_perf_users_count:
            if errors_count >= ERROR_LIMIT:
                raise Exception(f'ERROR: Maximum error limit reached {errors_count}/{ERROR_LIMIT}. '
                                f'Please check the errors in bzt.log')
            username = f"{DEFAULT_USER_PREFIX}{__generate_random_string(10)}"
            try:
                user = api.create_user(name=username, password=DEFAULT_USER_PASSWORD)
                print(f"User {user['name']} is created, number of users to create is "
                      f"{config_perf_users_count - len(cur_perf_user)}")
                cur_perf_user.append(user)
            # To avoid rate limit error from server. Execution should not be stopped after catch error from server.
            except Exception as error:
                print(f"Warning: Create jira user error: {error}. Retry limits {errors_count}/{ERROR_LIMIT}")
                errors_count = errors_count + 1
        print('All performance test users were successfully created')
        return cur_perf_user


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

    issues = [f"{issue['key']},{issue['id']},{issue['key'].split('-')[0]}" for issue in datasets[CUSTOM_ISSUES]]
    __write_to_file(JIRA_DATASET_CUSTOM_ISSUES, issues)

    keys = datasets[PROJECTS]
    __write_to_file(JIRA_DATASET_PROJECTS, keys)


def __create_data_set(jira_api):
    dataset = dict()
    dataset[USERS] = __get_users(jira_api)
    perf_user = random.choice(dataset[USERS])
    perf_user_api = JiraRestClient(JIRA_SETTINGS.server_url, perf_user['name'], DEFAULT_USER_PASSWORD)
    software_projects = __get_software_projects(perf_user_api)
    dataset[PROJECTS] = software_projects
    dataset[ISSUES] = __get_issues(perf_user_api, software_projects)
    dataset[CUSTOM_ISSUES] = __get_custom_issues(perf_user_api, JIRA_SETTINGS.custom_dataset_query)
    dataset[SCRUM_BOARDS] = __get_boards(perf_user_api, 'scrum')
    dataset[KANBAN_BOARDS] = __get_boards(perf_user_api, 'kanban')
    dataset[JQLS] = __generate_jqls(count=150)
    print(f'Users count: {len(dataset[USERS])}')
    print(f'Projects: {len(dataset[PROJECTS])}')
    print(f'Issues count: {len(dataset[ISSUES])}')
    print(f'Scrum boards count: {len(dataset[SCRUM_BOARDS])}')
    print(f'Kanban boards count: {len(dataset[KANBAN_BOARDS])}')
    print(f'Jqls count: {len(dataset[JQLS])}')
    print('------------------------')
    print(f'Custom dataset issues: {len(dataset[CUSTOM_ISSUES])}')

    return dataset


def __get_issues(jira_api, software_projects):
    project_keys = [f"{prj.split(',')[0]}" for prj in software_projects]
    jql_projects_str = ','.join(f'"{prj_key}"' for prj_key in project_keys)
    issues = jira_api.issues_search(
        jql=f"project in ({jql_projects_str}) AND status != Closed order by key", max_results=8000
    )
    if not issues:
        raise SystemExit(f"There are no issues in Jira accessible by a random performance user: {jira_api.user}")

    return issues


def __get_custom_issues(jira_api, custom_jql):
    issues = []
    if custom_jql:
        issues = jira_api.issues_search(
            jql=custom_jql, max_results=8000
        )
        if not issues:
            print(f"There are no issues found using JQL {custom_jql}")
    return issues


def __get_boards(jira_api, board_type):
    boards = jira_api.get_boards(board_type=board_type, max_results=250)
    if not boards:
        raise SystemExit(
            f"There are no {board_type} boards in Jira accessible by a random performance user: {jira_api.user}")

    return boards


def __get_users(jira_api):
    perf_users = jira_api.get_users(username=DEFAULT_USER_PREFIX, max_results=performance_users_count)
    users = generate_perf_users(api=jira_api, cur_perf_user=perf_users)
    if not users:
        raise SystemExit(f"There are no users in Jira accessible by a random performance user: {jira_api.user}")

    return users


def __get_software_projects(jira_api):
    all_projects = jira_api.get_all_projects()
    software_projects = \
        [f"{project['key']},{project['id']}" for project in all_projects if 'software' == project.get('projectTypeKey')]
    if not software_projects:
        raise SystemExit(
            f"There are no software projects in Jira accessible by a random performance user: {jira_api.user}")
    return software_projects


def __check_current_language(jira_api):
    language = jira_api.get_locale()
    if language != ENGLISH:
        raise SystemExit(f'"{language}" language is not supported. '
                         f'Please change your profile language to "English (United States) [Default]"')


def __check_for_admin_permissions(jira_api):
    user_permissions = jira_api.get_user_permissions()
    if not (user_permissions['permissions']['ADMINISTER']['havePermission'] or
            user_permissions['permissions']['SYSTEM_ADMIN']['havePermission']):
        raise SystemExit(f"The '{jira_api.user}' user does not have admin permissions.")


def main():
    print("Started preparing data")

    url = JIRA_SETTINGS.server_url
    print("Server url: ", url)

    client = JiraRestClient(url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password, verify=JIRA_SETTINGS.secure)

    __check_for_admin_permissions(client)
    __check_current_language(client)
    dataset = __create_data_set(client)
    write_test_data_to_files(dataset)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
