from pathlib import Path


def __get_jira_yml():
    return Path(__file__).parents[1] / "jira.yml"


def __get_datasets():
    return Path(__file__).parents[1] / "datasets"


def __get_jira_datasets():
    return __get_datasets() / "jira"


def __get_jira_dataset(file_name):
    return __get_jira_datasets() / file_name


def __get_confluence_yml():
    return Path(__file__).parents[1] / "confluence.yml"


def __get_bitbucket_yml():
    return Path(__file__).parents[1] / "bitbucket.yml"


def __get_bitbucket_datasets():
    return __get_datasets() / "bitbucket"


def __get_confluence_datasets():
    return __get_datasets() / "confluence"


def __get_confluence_dataset(file_name):
    return __get_confluence_datasets() / file_name


def __get_bitbucket_dataset(file_name):
    return __get_bitbucket_datasets() / file_name


JIRA_YML = __get_jira_yml()
JIRA_DATASETS = __get_jira_datasets()
JIRA_DATASET_JQLS = __get_jira_dataset('jqls.csv')
JIRA_DATASET_SCRUM_BOARDS = __get_jira_dataset('scrum-boards.csv')
JIRA_DATASET_KANBAN_BOARDS = __get_jira_dataset('kanban-boards.csv')
JIRA_DATASET_USERS = __get_jira_dataset('users.csv')
JIRA_DATASET_ISSUES = __get_jira_dataset('issues.csv')
JIRA_DATASET_PROJECT_KEYS = __get_jira_dataset('project_keys.csv')

CONFLUENCE_YML = __get_confluence_yml()
CONFLUENCE_DATASETS = __get_confluence_datasets()
CONFLUENCE_USERS = __get_confluence_dataset('users.csv')
CONFLUENCE_PAGES = __get_confluence_dataset('pages.csv')
CONFLUENCE_BLOGS = __get_confluence_dataset('blogs.csv')

BITBUCKET_YML = __get_bitbucket_yml()
BITBUCKET_DATASETS = __get_bitbucket_datasets()
BITBUCKET_USERS = __get_bitbucket_dataset('users.csv')
BITBUCKET_PROJECTS = __get_bitbucket_dataset('projects.csv')
BITBUCKET_REPOS = __get_bitbucket_dataset('repos.csv')
BITBUCKET_PRS = __get_bitbucket_dataset('pull_requests.csv')
