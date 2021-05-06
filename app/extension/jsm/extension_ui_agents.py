from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jsm.pages.agent_pages import Login
from util.conf import JSM_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_issues']:
        issue_key = datasets['custom_issue_key']

    @print_timing("selenium_agent_app_custom_action")
    def measure():

        @print_timing("selenium_agent_app_custom_action:view_request")
        def sub_measure():
            page.go_to_url(f"{JSM_SETTINGS.server_url}/browse/{issue_key}")
            # Wait for summary field visible
            page.wait_until_visible((By.ID, "summary-val"))
            # Wait for you app-specific UI element by ID selector
            page.wait_until_visible((By.ID, "ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT"))
        sub_measure()
    measure()


def app_specific_action_notification_config_web_action_support(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_agent_app_custom_action_notification_config_web_action_support")
    def measure():

        @print_timing("selenium_agent_app_custom_action:notification_config_web_action_support")
        def sub_measure():
            page.go_to_url(f"{JSM_SETTINGS.server_url}/secure/NotificationsConfigWebActionSupport.jspa")
            page.wait_until_visible((By.ID, "project-filter"))
        sub_measure()
    measure()


def app_specific_action_notification_schema_web_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_agent_app_custom_action_notification_schema_web_action")
    def measure():

        @print_timing("selenium_agent_app_custom_action:notification_schema_web_action")
        def sub_measure():
            page.go_to_url(f"{JSM_SETTINGS.server_url}/secure/MFJSDCNotificationSchemaWebAction.jspa?projectKey=SDP")
            page.wait_until_visible((By.ID, "system-rules-table"))
        sub_measure()
    measure()
