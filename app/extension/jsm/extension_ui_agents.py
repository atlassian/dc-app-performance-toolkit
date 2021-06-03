from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jsm.pages.agent_pages import Login
from util.conf import JSM_SETTINGS


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
            page.go_to_url(f"{JSM_SETTINGS.server_url}/secure/MFJSDCNotificationSchemaWebAction.jspa?projectKey=IT")
            page.wait_until_visible((By.ID, "system-rules-table"))
        sub_measure()
    measure()
