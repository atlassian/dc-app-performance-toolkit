from selenium_ui.bamboo import modules
from extension.bamboo import extension_ui  # noqa F401


# this action should be the first one
def test_0_selenium_a_login(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.login(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_view_all_projects(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.view_all_projects(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_view_all_builds(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.view_all_builds(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_config_plan_page(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.config_plan(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_build_activity_queue(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.builds_queue_page(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_view_plan_summary(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.view_plan_summary(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_view_plan_history(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.view_plan_history_page(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_view_build_summary(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.view_build_summary(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_view_build_logs(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.view_build_logs(bamboo_webdriver, bamboo_datasets)


def test_1_selenium_view_job_configuration(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.view_job_configuration(bamboo_webdriver, bamboo_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/bamboo/extension_ui.py`.
Refer to `app/selenium_ui/bamboo/modules.py` for examples.
"""
# def test_1_selenium_custom_action(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
#     extension_ui.app_specific_action(bamboo_webdriver, bamboo_datasets)


# this action should be the last one
def test_2_selenium_z_log_out(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.log_out(bamboo_webdriver, bamboo_datasets)
