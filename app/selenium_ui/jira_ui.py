from selenium_ui.jira import modules
from extension.jira import extension_ui  # noqa F401


# this action should be the first one
def test_0_selenium_a_login(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.login(jira_webdriver, jira_datasets)


def test_1_selenium_browse_projects_list(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.browse_projects_list(jira_webdriver, jira_datasets)


def test_1_selenium_browse_boards_list(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.browse_boards_list(jira_webdriver, jira_datasets)

def test_1_selenium_create_issue(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.create_issue(jira_webdriver, jira_datasets)

def test_1_selenium_edit_issue(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.edit_issue(jira_webdriver, jira_datasets)

def test_1_selenium_save_comment(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.save_comment(jira_webdriver, jira_datasets)

def test_1_selenium_search_jql(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.search_jql(jira_webdriver, jira_datasets)

def test_1_selenium_view_backlog_for_scrum_board(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.view_backlog_for_scrum_board(jira_webdriver, jira_datasets)

def test_1_selenium_view_scrum_board(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.view_scrum_board(jira_webdriver, jira_datasets)

def test_1_selenium_view_kanban_board(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.view_kanban_board(jira_webdriver, jira_datasets)

def test_1_selenium_view_dashboard(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.view_dashboard(jira_webdriver, jira_datasets)

def test_1_selenium_view_issue(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.view_issue(jira_webdriver, jira_datasets)

def test_1_selenium_view_project_summary(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.view_project_summary(jira_webdriver, jira_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jira/extension_ui.py`.
Refer to `app/selenium_ui/jira/modules.py` for examples.
"""
def test_1_selenium_b_custom_action(jira_webdriver, jira_datasets, jira_screen_shots):
    extension_ui.app_specific_action(jira_webdriver, jira_datasets)
  
def test_1_selenium_c_app_test_suites_page(jira_webdriver, jira_datasets):
    extension_ui.navigate_to_test_suite_page(jira_webdriver, jira_datasets)

def test_1_selenium_d_app_traceability_page(jira_webdriver):
    extension_ui.navigate_to_traceability_report_page(jira_webdriver)

def test_1_selenium_e_app_reports_page(jira_webdriver):
    extension_ui.navigate_to_app_report_page(jira_webdriver)

def test_1_selenium_f_app_my_settings_page(jira_webdriver):
    extension_ui.navigate_to_my_settings_page(jira_webdriver)

# this action should be the last one
def test_2_selenium_z_log_out(jira_webdriver, jira_datasets, jira_screen_shots):
    modules.log_out(jira_webdriver, jira_datasets)
