from pathlib import Path


def __get_jira_yml():
    return Path(__file__).parents[1] / "jira.yml"


def __get_datasets():
    return Path(__file__).parents[1] / "datasets"


def __get_jira_datasets():
    return __get_datasets() / "jira"


JIRA_YML = __get_jira_yml()
JIRA_DATASETS = __get_jira_datasets()
