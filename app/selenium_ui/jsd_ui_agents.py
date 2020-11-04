from selenium_ui.jsd import modules_agents
from extension.jira import extension_ui  # TODO develop example of app-specific action for JSD


# this action should be the first one
def test_0_customer_selenium_a_login(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.login(jsd_webdriver, jsd_datasets)


def test_1_selenium_browse_projects_list(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.browse_projects_list(jsd_webdriver, jsd_datasets)


def test_1_selenium_browse_project_customers_page(jsd_webdriver, jsd_datasets, jsd_screen_shots):
    modules_agents.browse_project_customers_page(jsd_webdriver, jsd_datasets)


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
