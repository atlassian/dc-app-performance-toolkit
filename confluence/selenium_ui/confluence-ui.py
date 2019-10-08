from confluence.selenium_ui.modules import *
from confluence.extension.extension_ui import *


# this action should be the first one
def test_0_selenium_a_login(webdriver, datasets, screen_shots):
    login(webdriver, datasets)


def test_1_selenium_view_page(webdriver, datasets, screen_shots):
    view_page(webdriver, datasets)


def test_1_selenium_create_page(webdriver, datasets, screen_shots):
    create_page(webdriver, datasets)


def test_1_selenium_edit_page(webdriver, datasets, screen_shots):
    edit_page(webdriver, datasets)


def test_1_selenium_create_comment(webdriver, datasets, screen_shots):
    create_comment(webdriver, datasets)


def test_1_selenium_view_blog(webdriver, datasets, screen_shots):
    view_blog(webdriver, datasets)


def test_1_selenium_view_dashboard(webdriver, datasets, screen_shots):
    view_dashboard(webdriver, datasets)


""" Add custom actions anywhere between login and log out action. Move this to a different line as needed.
    Write your custom selenium scripts in `../extension/extension.py`. Refer to `modules.py` for examples.
"""
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     custom_action(webdriver, datasets)


# this action should be the last one
def test_2_selenium_z_log_out(webdriver, datasets, screen_shots):
    log_out(webdriver, datasets)
