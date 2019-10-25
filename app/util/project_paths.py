from pathlib import Path


def __get_jira_yml():
    return Path(__file__).parents[1] / "jira.yml"


def __get_datasets():
    return Path(__file__).parents[1] / "datasets"


def __get_jira_datasets():
    return __get_datasets() / "jira"


def __get_jira_dataset(file_name):
    return __get_jira_datasets() / file_name


def __get_jira_dataset_jqls():
    return __get_jira_dataset('jqls.csv')


def __get_jira_dataset_scrum_boards():
    return __get_jira_dataset('scrum-boards.csv')


def __get_jira_dataset_kanban_boards():
    return __get_jira_dataset('kanban-boards.csv')


def __get_jira_dataset_users():
    return __get_jira_dataset('users.csv')


def __get_jira_dataset_issues():
    return __get_jira_dataset('issues.csv')

def __get_jira_projects_key():
    return __get_jira_dataset('project_keys.csv')

def __get_confluence_yml():
    return Path(__file__).parents[1] / "confluence.yml"


JIRA_YML = __get_jira_yml()
JIRA_DATASETS = __get_jira_datasets()
JIRA_DATASET_JQLS = __get_jira_dataset_jqls()
JIRA_DATASET_SCRUM_BOARDS = __get_jira_dataset_scrum_boards()
JIRA_DATASET_KANBAN_BOARDS = __get_jira_dataset_kanban_boards()
JIRA_DATASET_USERS = __get_jira_dataset_users()
JIRA_DATASET_ISSUES = __get_jira_dataset_issues()
JIRA_DATASET_PROJECT_KEYS = __get_jira_projects_key()

CONFLUENCE_YML = __get_confluence_yml()
