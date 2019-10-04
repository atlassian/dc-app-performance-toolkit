# Work around import issue
import os
import random
import string
import sys

import yaml

# TODO fix this work around
from util.project_paths import JIRA_DATASETS, JIRA_YML

sys.path.insert(0, os.getcwd())
print("System path: ", sys.path)

from util.data_preparation.jira.api import ApiJira

DEFAULT_USER_PASSWORD = 'password'
DEFAULT_USER_PREFIX = 'performance_'


def generate_jqls(max_length=3, count=100):
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
    datasets_path = JIRA_DATASETS

    def write_to_file(file_name, list):
        with open(datasets_path / file_name, 'w') as f:
            for item in list:
                f.write(f"{item}\n")

    write_to_file('jqls.csv', datasets['jqls'])

    scrum_boards = [f"{board['id']}" for board in datasets['boards'] if board['type'] == 'scrum']
    write_to_file('scrum-boards.csv', scrum_boards)

    kanban_boards = [f"{board['id']}" for board in datasets['boards'] if board['type'] == 'kanban']
    write_to_file('kanban-boards.csv', kanban_boards)

    users = [f"{user['name']},{DEFAULT_USER_PASSWORD}" for user in datasets['users']]
    write_to_file('users.csv', users)

    issues = [f"{issue['key']},{issue['id']},{issue['key'].split('-')[0]}" for issue in datasets['issues']]
    write_to_file('issues.csv', issues)


def main():
    print("Started preparing data")

    # TODO consider getting server url from jira.yml see get_perf_users_count()
    url = sys.argv[1]
    print("Server url: ", url)

    dataset = dict()

    # TODO consider reading jira.yml only once
    with JIRA_YML.open(mode='r') as file:
        jira_yaml = yaml.load(file, Loader=yaml.FullLoader)
        user, password = jira_yaml['settings']['env']['admin_login'], jira_yaml['settings']['env']['admin_password']

    jira_api = ApiJira(url, user, password)
    dataset["boards"] = jira_api.get_boards(type='scrum', maxResults=250) \
                        + jira_api.get_boards(type='kanban', maxResults=250)

    perf_users = jira_api.get_users(username=DEFAULT_USER_PREFIX, maxResults=performance_users_count)
    dataset["users"] = generate_perf_users(api=jira_api, cur_perf_user=perf_users)

    dataset["issues"] = jira_api.issues_search(jql="status != Closed order by key", maxResults=8000)
    dataset["jqls"] = generate_jqls(count=150)

    write_test_data_to_files(dataset)


if __name__ == "__main__":
    main()
