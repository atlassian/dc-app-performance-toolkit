from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jsm.pages.agent_pages import Login
from util.conf import JSM_SETTINGS


def insight_app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['insight_schemas']:
        schema_id = datasets['schema_id']

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action

    @print_timing("selenium_app_specific_user_login")
    def measure():
        def app_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.set_credentials(username=username, password=password)
            if login_page.is_first_login():
                login_page.first_login_setup()
            if login_page.is_first_login_second_page():
                login_page.first_login_second_page_setup()
            login_page.wait_for_page_loaded()
        app_specific_user_login(username='admin', password='admin')
    measure()

    @print_timing("selenium_insight_app_custom_action")
    def measure():

        @print_timing("selenium_insight_app_custom_action:view_random_schema")
        def sub_measure():
            page.go_to_url(f"{JSM_SETTINGS.server_url}/secure/ObjectSchema.jspa?id={schema_id}")
            # Wait for summary field of schema visible
            page.wait_until_visible((By.ID, "rlabs-create-object"))
            # Wait for you app-specific UI element by ID selector
            # page.wait_until_visible((By.ID, "ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT"))
        sub_measure()
    measure()
