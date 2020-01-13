from selenium_ui.bitbucket import modules
from extension.jira import extension_ui


# this action should be the first one
def test_0_selenium_a_login(webdriver, bitbucket_datasets, jira_screen_shots):
    modules.login(webdriver, bitbucket_datasets)


# def test_1_selenium_view_dashboard(webdriver, bitbucket_datasets, jira_screen_shots):
#     modules.view_dashboard(webdriver, bitbucket_datasets)
#
#
# def test_2_selenium_view_projects(webdriver, bitbucket_datasets, jira_screen_shots):
#     modules.view_projects(webdriver, bitbucket_datasets)
#
#
# def test_3_selenium_view_project_repositories(webdriver, bitbucket_datasets, jira_screen_shots):
#     modules.view_project_repos(webdriver, bitbucket_datasets)


def test_4_selenium_browse_repo(webdriver, bitbucket_datasets, jira_screen_shots):
    modules.view_repo(webdriver, bitbucket_datasets)


def test_5_selenium_browse_pull_request_overview(webdriver, bitbucket_datasets, jira_screen_shots):
    modules.view_pr_overview(webdriver, bitbucket_datasets)