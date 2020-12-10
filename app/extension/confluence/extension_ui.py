from selenium.webdriver.common.by import By
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS

from selenium_ui.base_page import BasePage


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:shared_pages")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugins/sharedPages/shared.action")
            page.wait_until_visible((By.ID, "overviewTable"))  # Wait for overview visible
        sub_measure()
    measure()