from selenium_ui.bitbucket import modules
from extension.bitbucket import extension_ui


# this action should be the first one
def test_0_selenium_a_login(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.login(webdriver, bitbucket_datasets)


def test_1_selenium_view_dashboard(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_dashboard(webdriver, bitbucket_datasets)


def test_2_selenium_create_pull_request(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.create_pull_request(webdriver, bitbucket_datasets)


def test_3_selenium_view_projects(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_projects(webdriver, bitbucket_datasets)


def test_4_selenium_view_project_repositories(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_project_repos(webdriver, bitbucket_datasets)


def test_5_selenium_view_repo(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_repo(webdriver, bitbucket_datasets)


def test_6_selenium_view_list_pull_requests(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_list_pull_requests(webdriver, bitbucket_datasets)


def test_7_selenium_view_pull_request_overview(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_pull_request_overview_tab(webdriver, bitbucket_datasets)


def test_8_selenium_view_pull_request_diff(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_pull_request_diff_tab(webdriver, bitbucket_datasets)


def test_9_selenium_view_pull_request_commits(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_pull_request_commits_tab(webdriver, bitbucket_datasets)


def test_10_selenium_comment_pull_request_diff(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.comment_pull_request_diff(webdriver, bitbucket_datasets)


def test_11_selenium_comment_pull_request_overview(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.comment_pull_request_overview(webdriver, bitbucket_datasets)


def test_12_selenium_view_branches(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_branches(webdriver, bitbucket_datasets)


def test_13_selenium_view_commits(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_commits(webdriver, bitbucket_datasets)


# def test_01_selenium_create_pull_request(webdriver, bitbucket_datasets, bitbucket_screen_shots):
#     modules.create_pull_request(webdriver, bitbucket_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jira/extension_ui.py`. 
Refer to `app/selenium_ui/jira/modules.py` for examples.
"""
# def test_1_selenium_custom_action(webdriver, bitbucket_datasets, bitbucket_screen_shots):
#     extension_ui.custom_action(webdriver, bitbucket_datasets)


def test_14_selenium_logout(webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.logout(webdriver, bitbucket_datasets)
