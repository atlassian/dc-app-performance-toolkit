from selenium.webdriver.common.by import By
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS

from selenium_ui.base_page import BasePage


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)

    @print_timing("selenium_app_custom_action2")
    def measure():

        @print_timing("selenium_app_custom_action2:read_confirmations")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugins/readConfirmation/readConfirmations.action")
            page.wait_until_visible((By.ID, "app"))  # Wait for title field visible
        sub_measure()
    measure()
