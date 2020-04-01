from selenium_ui.jira import modules
from extension.jira import extension_ui


# this action should be the first one
def test_0_selenium_a_login(webdriver, jira_datasets, jira_screen_shots):
    modules.login(webdriver, jira_datasets)


def test_1_selenium_browse_projects_list(webdriver, jira_datasets, jira_screen_shots):
    modules.browse_projects_list(webdriver, jira_datasets)


def test_1_selenium_browse_boards_list(webdriver, jira_datasets, jira_screen_shots):
    modules.browse_boards_list(webdriver, jira_datasets)


def test_1_selenium_create_issue(webdriver, jira_datasets, jira_screen_shots):
    modules.create_issue(webdriver, jira_datasets)


def test_1_selenium_edit_issue(webdriver, jira_datasets, jira_screen_shots):
    modules.edit_issue(webdriver, jira_datasets)


def test_1_selenium_save_comment(webdriver, jira_datasets, jira_screen_shots):
    modules.save_comment(webdriver, jira_datasets)


def test_1_selenium_search_jql(webdriver, jira_datasets, jira_screen_shots):
    modules.search_jql(webdriver, jira_datasets)


def test_1_selenium_view_backlog_for_scrum_board(webdriver, jira_datasets, jira_screen_shots):
    modules.view_backlog_for_scrum_board(webdriver, jira_datasets)


def test_1_selenium_view_scrum_board(webdriver, jira_datasets, jira_screen_shots):
    modules.view_scrum_board(webdriver, jira_datasets)


def test_1_selenium_view_kanban_board(webdriver, jira_datasets, jira_screen_shots):
    modules.view_kanban_board(webdriver, jira_datasets)


def test_1_selenium_view_dashboard(webdriver, jira_datasets, jira_screen_shots):
    modules.view_dashboard(webdriver, jira_datasets)


def test_1_selenium_view_issue(webdriver, jira_datasets, jira_screen_shots):
    modules.view_issue(webdriver, jira_datasets)


def test_1_selenium_view_project_summary(webdriver, jira_datasets, jira_screen_shots):
    modules.view_project_summary(webdriver, jira_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jira/extension_ui.py`. 
Refer to `app/selenium_ui/jira/modules.py` for examples.
"""
# def test_1_selenium_custom_action(webdriver, jira_datasets, jira_screen_shots):
#     extension_ui.custom_action(webdriver, jira_datasets)


# this action should be the last one
def test_2_selenium_z_log_out(webdriver, jira_datasets, jira_screen_shots):
    modules.log_out(webdriver, jira_datasets)
