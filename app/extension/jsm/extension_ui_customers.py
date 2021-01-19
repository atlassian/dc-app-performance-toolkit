from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import JSM_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_issues']:
        custom_request_key = datasets['custom_issue_key']
        custom_service_desk_id = datasets['custom_service_desk_id']

    @print_timing("selenium_customer_app_custom_action")
    def measure():

        @print_timing("selenium_customer_app_custom_action:view_request")
        def sub_measure():
            page.go_to_url(f"{JSM_SETTINGS.server_url}/servicedesk/customer/portal/"
                           f"{custom_service_desk_id}/{custom_request_key}")
            # Wait for options element visible
            page.wait_until_visible((By.CLASS_NAME, 'cv-request-options'))
            # Wait for you app-specific UI element by ID selector
            page.wait_until_visible((By.ID, "ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT"))
        sub_measure()
    measure()
