import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import JSM_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    customer_request_key = datasets['customer_request_key']
    customer_portal_id = datasets['customer_service_desk_id']

    @print_timing("selenium_customer_app_custom_action")
    def measure():

        @print_timing("selenium_customer_app_custom_action:view_request")
        def sub_measure():
            page.go_to_url(f"{JSM_SETTINGS.server_url}/servicedesk/customer/portal/{customer_portal_id}/{customer_request_key}")
            page.wait_until_visible((By.ID, "summary-val"))  # Wait for summary field visible
            page.wait_until_visible((By.ID, "ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT"))  # Wait for you app-specific UI element by ID selector
        sub_measure()
    measure()
