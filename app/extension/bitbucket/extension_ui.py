from selenium.webdriver.common.by import By
from selenium_ui.conftest import print_timing
from util.conf import BITBUCKET_SETTINGS

from selenium_ui.base_page import BasePage


def custom_action(webdriver, datasets):
    page = BasePage(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugin/report")
            page.wait_until_visible((By.ID, 'report_app_element_id'), interaction)

        measure(webdriver, 'selenium_app_custom_action:view_report')

        @print_timing
        def measure(webdriver, interaction):
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/plugin/dashboard")
            page.wait_until_visible((By.ID, 'dashboard_app_element_id'), interaction)

        measure(webdriver, 'selenium_app_custom_action:view_dashboard')
    measure(webdriver, 'selenium_app_custom_action')
