import datetime
import os
from pathlib import Path


def __get_jira_yml():
    return Path(__file__).parents[1] / "jira.yml"


def __get_jsm_yml():
    return Path(__file__).parents[1] / "jsm.yml"


def __get_datasets():
    return Path(__file__).parents[1] / "datasets"


def __get_jira_datasets():
    return __get_datasets() / "jira"


def __get_jsm_datasets():
    return __get_datasets() / "jsm"


def __get_jira_dataset(file_name):
    return __get_jira_datasets() / file_name


def __get_jsm_dataset(file_name):
    return __get_jsm_datasets() / file_name


def __get_confluence_yml():
    return Path(__file__).parents[1] / "confluence.yml"


def __get_bitbucket_yml():
    return Path(__file__).parents[1] / "bitbucket.yml"


def __get_bitbucket_datasets():
    return __get_datasets() / "bitbucket"


def __get_crowd_yml():
    return Path(__file__).parents[1] / "crowd.yml"


def __get_crowd_datasets():
    return __get_datasets() / "crowd"


def __get_crowd_dataset(file_name):
    return __get_crowd_datasets() / file_name


def __get_confluence_datasets():
    return __get_datasets() / "confluence"


def __get_confluence_dataset(file_name):
    return __get_confluence_datasets() / file_name


def __get_bitbucket_dataset(file_name):
    return __get_bitbucket_datasets() / file_name


def __get_taurus_artifacts_dir():
    if 'TAURUS_ARTIFACTS_DIR' in os.environ:
        return Path(os.environ.get('TAURUS_ARTIFACTS_DIR'))
    else:
        results_dir_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        local_run_results = Path(f'results/local/{results_dir_name}')
        local_run_results.mkdir(parents=True)
        return local_run_results


def __get_default_test_actions():
    return Path(__file__).parents[0] / "default_test_actions.json"


JIRA_YML = __get_jira_yml()
JIRA_DATASETS = __get_jira_datasets()
JIRA_DATASET_JQLS = __get_jira_dataset('jqls.csv')
JIRA_DATASET_SCRUM_BOARDS = __get_jira_dataset('scrum-boards.csv')
JIRA_DATASET_KANBAN_BOARDS = __get_jira_dataset('kanban-boards.csv')
JIRA_DATASET_USERS = __get_jira_dataset('users.csv')
JIRA_DATASET_ISSUES = __get_jira_dataset('issues.csv')
JIRA_DATASET_PROJECTS = __get_jira_dataset('projects.csv')
JIRA_DATASET_CUSTOM_ISSUES = __get_jira_dataset('custom-issues.csv')

JSM_YML = __get_jsm_yml()
JSM_DATASETS = __get_jsm_datasets()
JSM_DATASET_AGENTS = __get_jsm_dataset('agents.csv')
JSM_DATASET_CUSTOMERS = __get_jsm_dataset('customers.csv')
JSM_DATASET_REQUESTS = __get_jsm_dataset('requests.csv')
JSM_DATASET_SERVICE_DESKS_L = __get_jsm_dataset('service_desks_large.csv')
JSM_DATASET_SERVICE_DESKS_M = __get_jsm_dataset('service_desks_medium.csv')
JSM_DATASET_SERVICE_DESKS_S = __get_jsm_dataset('service_desks_small.csv')
JSM_DATASET_REQUEST_TYPES = __get_jsm_dataset('request_types.csv')
JSM_DATASET_CUSTOM_ISSUES = __get_jsm_dataset('custom-issues.csv')

CONFLUENCE_YML = __get_confluence_yml()
CONFLUENCE_DATASETS = __get_confluence_datasets()
CONFLUENCE_USERS = __get_confluence_dataset('users.csv')
CONFLUENCE_PAGES = __get_confluence_dataset('pages.csv')
CONFLUENCE_BLOGS = __get_confluence_dataset('blogs.csv')
CONFLUENCE_STATIC_CONTENT = __get_confluence_dataset('static-content/files_upload.csv')
CONFLUENCE_CUSTOM_PAGES = __get_confluence_dataset('custom_pages.csv')

BITBUCKET_YML = __get_bitbucket_yml()
BITBUCKET_DATASETS = __get_bitbucket_datasets()
BITBUCKET_USERS = __get_bitbucket_dataset('users.csv')
BITBUCKET_PROJECTS = __get_bitbucket_dataset('projects.csv')
BITBUCKET_REPOS = __get_bitbucket_dataset('repos.csv')
BITBUCKET_PRS = __get_bitbucket_dataset('pull_requests.csv')

CROWD_YML = __get_crowd_yml()
CROWD_DATASETS = __get_crowd_datasets()
CROWD_USERS = __get_crowd_dataset('users.csv')


DEFAULT_TEST_ACTIONS = __get_default_test_actions()
ENV_TAURUS_ARTIFACT_DIR = __get_taurus_artifacts_dir()
