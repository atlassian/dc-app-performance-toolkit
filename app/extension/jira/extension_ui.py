import pytest
from selenium_ui.jira import sfj_modules


from selenium_ui.jira_ui import test_0_selenium_a_login

def test_1_selenium_edit_skillset(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.edit_skillset(jira_webdriver, jira_datasets)

def test_1_selenium_view_skillset(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.view_skillset(jira_webdriver, jira_datasets)

def test_1_selenium_open_expert_finder(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.open_expert_finder(jira_webdriver, jira_datasets)


def test_1_selenium_click_expert_finder_node(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.click_expert_finder_node(jira_webdriver, jira_datasets)

def test_1_selenium_open_assignments_dashboard(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.open_assignments_dashboard(jira_webdriver, jira_datasets)

def test_1_selenium_pull_assignment(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.pull_assignment(jira_webdriver, jira_datasets)

def test_1_selenium_open_inspector(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.open_inspector(jira_webdriver, jira_datasets)
def test_1_selenium_inspector_select_user(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.inspector_select_user(jira_webdriver, jira_datasets)

def test_1_selenium_open_risk_analysis(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.open_risk_analysis(jira_webdriver, jira_datasets)
def test_1_selenium_run_risk_analysis(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.run_risk_analysis(jira_webdriver, jira_datasets)
def test_1_selenium_open_simulation(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.open_simulation(jira_webdriver, jira_datasets)
def test_1_selenium_run_simulation(jira_webdriver, jira_datasets, jira_screen_shots):
    sfj_modules.run_simulation(jira_webdriver, jira_datasets)


# def app_specific_action(webdriver, datasets):
#     page = BasePage(webdriver)
#     if datasets['custom_issues']:
#         issue_key = datasets['custom_issue_key']

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action
    #
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.set_credentials(username=username, password=password)
    #         if login_page.is_first_login():
    #             login_page.first_login_setup()
    #         if login_page.is_first_login_second_page():
    #             login_page.first_login_second_page_setup()
    #         login_page.wait_for_page_loaded()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    # @print_timing("selenium_app_custom_action")
    # def measure():
    #     @print_timing("selenium_app_custom_action:view_issue")
    #     def sub_measure():
    #         page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_key}")
    #         page.wait_until_visible((By.ID, "summary-val"))  # Wait for summary field visible
    #         page.wait_until_visible((By.ID, "ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT"))  # Wait for you app-specific UI element by ID selector
    #     sub_measure()
    # measure()

