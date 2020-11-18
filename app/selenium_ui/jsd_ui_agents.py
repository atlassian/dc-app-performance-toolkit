from selenium_ui.jsd import modules_agents
from extension.jira import extension_ui  # TODO develop example of app-specific action for JSD


# this action should be the first one
def test_0_customer_selenium_a_login(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.login(jsd_webdriver, jsd_datasets)


def test_1_selenium_browse_service_desk_projects_list(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.browse_service_desk_projects_list(jsd_webdriver, jsd_datasets)


def test_1_selenium_browse_project_customers_page(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.browse_project_customers_page(jsd_webdriver, jsd_datasets)


def test_1_selenium_view_customer_request(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.view_customer_request(jsd_webdriver, jsd_datasets)


def test_1_selenium_large_project_view_reports(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.large_project_view_reports(jsd_webdriver, jsd_datasets)


def test_1_selenium_small_project_view_reports(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.small_project_view_reports(jsd_webdriver, jsd_datasets)


def test_1_selenium_add_request_comment(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.add_request_comment(jsd_webdriver, jsd_datasets)


def test_1_selenium_view_queue_all_open_large_project(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.view_queue_large_project(jsd_webdriver, jsd_datasets)


def test_1_selenium_view_queue_all_open_small_project(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.view_queue_small_project(jsd_webdriver, jsd_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jsd/extension_ui.py`.
Refer to `app/selenium_ui/jsd/modules_customers.py` for examples.
"""
# def test_1_selenium_custom_action(jira_webdriver, jira_datasets, jira_screen_shots):
#     extension_ui.app_specific_action(jira_webdriver, jira_datasets)


# this action should be the last one
def test_2_customer_selenium_z_log_out(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.log_out(jsd_webdriver, jsd_datasets)
