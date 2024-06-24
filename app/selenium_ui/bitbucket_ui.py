from selenium_ui.bitbucket import modules
from extension.bitbucket import extension_ui  # noqa F401


# this action should be the first one
def test_0_selenium_a_login(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.login(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_list_pull_requests(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_list_pull_requests(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_pull_request_overview(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_pull_request_overview_tab(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_pull_request_diff(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_pull_request_diff_tab(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_pull_request_commits(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_pull_request_commits_tab(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_comment_pull_request_diff(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.comment_pull_request_diff(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_comment_pull_request_overview(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.comment_pull_request_overview(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_dashboard(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_dashboard(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_create_pull_request(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.create_pull_request(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_projects(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_projects(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_project_repositories(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_project_repos(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_repo(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_repo(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_branches(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_branches(bitbucket_webdriver, bitbucket_datasets)


def test_1_selenium_view_commits(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.view_commits(bitbucket_webdriver, bitbucket_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/bitbucket/extension_ui.py`.
Refer to `app/selenium_ui/bitbucket/modules.py` for examples.
"""
# def test_1_selenium_custom_action(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
#     extension_ui.app_specific_action(bitbucket_webdriver, bitbucket_datasets)


def test_2_selenium_logout(bitbucket_webdriver, bitbucket_datasets, bitbucket_screen_shots):
    modules.logout(bitbucket_webdriver, bitbucket_datasets)
