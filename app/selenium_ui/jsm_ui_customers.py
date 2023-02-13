from selenium_ui.jsm import modules_customers
from extension.jsm import extension_ui_customers  # noqa F401
from util.conf import JSM_SETTINGS
import pytest


# this action should be the first one
def test_0_selenium_customer_a_login(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.login(jsm_webdriver, jsm_datasets)


def test_1_selenium_customer_create_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.create_request(jsm_webdriver, jsm_datasets)


def test_1_selenium_customer_view_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.view_request(jsm_webdriver, jsm_datasets)


def test_1_selenium_customer_view_requests(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.view_requests(jsm_webdriver, jsm_datasets)


def test_1_selenium_customer_view_all_requests(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.view_all_requests(jsm_webdriver, jsm_datasets)


def test_1_selenium_customer_share_request_with_customer(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.share_request_with_customer(jsm_webdriver, jsm_datasets)


def test_1_selenium_customer_add_comment(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.add_comment(jsm_webdriver, jsm_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jsm/extension_ui_customers.py`.
Refer to `app/selenium_ui/jsm/modules_customers.py` for examples.
"""


# # def test_1_selenium_customer_custom_action(jsm_webdriver, jsm_datasets, jsm_screen_shots):
# #     extension_ui_customers.app_specific_action(jsm_webdriver, jsm_datasets)

"""
To enable specific test for Insight below, set 'True' next to `insight` variable (False by default) in  `app/jsm.yml`
"""


def test_0_selenium_customer_insight_view_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if not JSM_SETTINGS.insight:
        pytest.skip()
    modules_customers.view_request_with_insight(jsm_webdriver, jsm_datasets)


# this action should be the last one
def test_2_selenium_customer_z_log_out(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_customers.log_out(jsm_webdriver, jsm_datasets)
