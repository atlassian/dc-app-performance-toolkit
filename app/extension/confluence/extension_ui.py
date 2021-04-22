import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.confluence.pages.pages import Login, AllUpdates
from util.conf import CONFLUENCE_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_pages']:
        app_specific_page_id = datasets['custom_page_id']

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.wait_for_page_loaded()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.click_login_button()
    #         if login_page.is_first_login():
    #             login_page.first_user_setup()
    #         all_updates_page = AllUpdates(webdriver)
    #         all_updates_page.wait_for_page_loaded()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:view_page")
        def sub_measure():
            page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/pages/viewpage.action?pageId={app_specific_page_id}")
            page.wait_until_visible((By.ID, "title-text"))  # Wait for title field visible
            page.wait_until_visible((By.ID, "ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT"))  # Wait for you app-specific UI element by ID selector
        sub_measure()
    measure()

def zscale_view_test_cases_by_status_macro_in_page(webdriver, datasets):
    page = BasePage(webdriver)
    zscale_specific_page_id = datasets['custom_page_id']

    @print_timing("zscale_specific_user_login")
    def measure():
        def zscale_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.wait_for_page_loaded()
            login_page.set_credentials(username=username, password=password)
            login_page.click_login_button()
            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
        zscale_specific_user_login(username='admin', password='admin')
    measure()

    @print_timing("view_test_cases_by_status_action")
    def measure():
        check_zscale_content(page, datasets)
    measure()

def zscale_view_test_cases_by_project_macro_in_page(webdriver, datasets):
    page = BasePage(webdriver)
    zscale_specific_page_id = datasets['custom_page_id']

    @print_timing("zscale_specific_user_login")
    def measure():
        def zscale_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.wait_for_page_loaded()
            login_page.set_credentials(username=username, password=password)
            login_page.click_login_button()
            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
        zscale_specific_user_login(username='admin', password='admin')
    measure()

    @print_timing("view_test_cases_by_project_action")
    def measure():
        check_zscale_content(page, datasets)
    measure()

def zscale_view_test_cases_by_folder_macro_in_page(webdriver, datasets):
    page = BasePage(webdriver)
    zscale_specific_page_id = datasets['custom_page_id']

    @print_timing("zscale_specific_user_login")
    def measure():
        def zscale_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.wait_for_page_loaded()
            login_page.set_credentials(username=username, password=password)
            login_page.click_login_button()
            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
        zscale_specific_user_login(username='admin', password='admin')
    measure()

    @print_timing("view_test_cases_by_folder_action")
    def measure():
        check_zscale_content(page, datasets)
    measure()


def check_zscale_content(page, datasets):
    zscale_specific_page_id = datasets['custom_page_id']
    
    page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/pages/viewpage.action?pageId={zscale_specific_page_id}")

    if zscale_specific_page_id == 38928401:
        page.wait_until_visible((By.TAG_NAME, "reports-viewer-test-cases-summary-by-status"))  
    elif zscale_specific_page_id == 38928403:
        page.wait_until_visible((By.TAG_NAME, "reports-viewer-test-cases-created-by-project-list")) 
    elif zscale_specific_page_id == 38928405:
        page.wait_until_visible((By.TAG_NAME, "reports-viewer-test-cases-created-by-folder-list")) 
    else:
        page.wait_until_visible((By.TAG_NAME, "macro-view"))  
