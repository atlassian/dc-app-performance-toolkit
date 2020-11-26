from selenium_ui.jsm import modules_customers
from extension.jira import extension_ui  # TODO develop example of app-specific action for jsm


# this action should be the first one
def test_0_customer_selenium_a_login(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.login(jsm_webdriver, jsm_datasets)


def test_1_customer_selenium_create_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.create_request(jsm_webdriver, jsm_datasets)


def test_1_customer_selenium_view_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.view_customer_request(jsm_webdriver, jsm_datasets)


def test_1_customer_selenium_my_requests(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.view_my_requests(jsm_webdriver, jsm_datasets)


def test_1_customer_selenium_all_requests(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.view_all_requests(jsm_webdriver, jsm_datasets)


def test_1_customer_selenium_share_customer_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.share_customer_request(jsm_webdriver, jsm_datasets)


def test_1_customer_selenium_comment_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.comment_customer_request(jsm_webdriver, jsm_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jsm/extension_ui.py`.
Refer to `app/selenium_ui/jsm/modules_customers.py` for examples.
"""
# def test_1_selenium_custom_action(jira_webdriver, jira_datasets, jira_screen_shots):
#     extension_ui.app_specific_action(jira_webdriver, jira_datasets)


# this action should be the last one
def test_2_customer_selenium_z_log_out(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.log_out(jsm_webdriver, jsm_datasets)
