from jira.selenium_ui.modules import *
from jira.extension.extension_ui import *


# this action should be the first one
def test_0_selenium_a_login(webdriver, datasets, screen_shots):
    login(webdriver, datasets)


def test_1_selenium_browse_project(webdriver, datasets, screen_shots):
    browse_project(webdriver, datasets)


def test_1_selenium_browse_board(webdriver, datasets, screen_shots):
    browse_board(webdriver, datasets)


def test_1_selenium_create_issue(webdriver, datasets, screen_shots):
    create_issue(webdriver, datasets)


def test_1_selenium_edit_issue(webdriver, datasets, screen_shots):
    edit_issue(webdriver, datasets)


def test_1_selenium_save_comment(webdriver, datasets, screen_shots):
    save_comment(webdriver, datasets)


def test_1_selenium_search_jql(webdriver, datasets, screen_shots):
    search_jql(webdriver, datasets)


def test_1_selenium_view_backlog_for_scrum_board(webdriver, datasets, screen_shots):
    view_backlog_for_scrum_board(webdriver, datasets)


def test_1_selenium_view_scrum_board(webdriver, datasets, screen_shots):
    view_scrum_board(webdriver, datasets)


def test_1_selenium_view_kanban_board(webdriver, datasets, screen_shots):
    view_kanban_board(webdriver, datasets)


def test_1_selenium_view_dashboard(webdriver, datasets, screen_shots):
    view_dashboard(webdriver, datasets)


def test_1_selenium_view_issue(webdriver, datasets, screen_shots):
    view_issue(webdriver, datasets)


def test_1_selenium_view_project_summary(webdriver, datasets, screen_shots):
    view_project_summary(webdriver, datasets)


""" Add custom actions anywhere between login and log out action. Move this to a different line as needed.
    Write your custom selenium scripts in `../extension/extension.py`. Refer to `modules.py` for examples.
"""
# def test_1_selenium_custom_action(webdriver, datasets, screen_shots):
#     custom_action(webdriver, datasets)


# this action should be the last one
def test_2_selenium_z_log_out(webdriver, datasets, screen_shots):
    log_out(webdriver, datasets)
