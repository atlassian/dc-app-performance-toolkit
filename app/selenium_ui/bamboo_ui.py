from selenium_ui.bamboo import modules
from extension.bamboo import extension_ui  # noqa F401


# this action should be the first one
def test_0_selenium_a_login(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.login(bamboo_webdriver, bamboo_datasets)


# # this action should be the last one
def test_2_selenium_z_log_out(bamboo_webdriver, bamboo_datasets, bamboo_screen_shots):
    modules.log_out(bamboo_webdriver, bamboo_datasets)
