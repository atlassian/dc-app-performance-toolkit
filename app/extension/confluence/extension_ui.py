from selenium.webdriver.common.by import By
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS

from selenium_ui.base_page import BasePage
from selenium_ui.confluence.pages.pages import Page, Editor


# def app_specific_action(webdriver, confluence_dataset, confluence_screen_shots):
#     page = BasePage(webdriver)
#
#     @print_timing("selenium_app_custom_action")
#     def measure():
#
#         @print_timing("selenium_app_custom_action:view_report")
#         def sub_measure():
#             page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugin/report")
#             page.wait_until_visible((By.ID, 'report_app_element_id'))
#         sub_measure()
#
#         @print_timing("selenium_app_custom_action:view_dashboard")
#         def sub_measure():
#             page.go_to_url(f"{CONFLUENCE_SETTINGS.server_url}/plugin/dashboard")
#             page.wait_until_visible((By.ID, 'dashboard_app_element_id'))
#         sub_measure()
#     measure()


def view_page_custom_page(webdriver, confluence_dataset):
    page = Page(webdriver, page_id=confluence_dataset['custom_page_id'])

    @print_timing("selenium_view_custom_page")
    def measure():
        page.go_to()
        page.wait_for_page_loaded()
    measure()


def edit_confluence_page(webdriver, confluence_dataset):
    edit_page = Editor(webdriver, page_id=confluence_dataset['custom_page_id'])

    @print_timing("selenium_edit_custom_page")
    def measure():

        @print_timing("selenium_edit_custom_page:open_create_page_editor")
        def sub_measure():
            edit_page.go_to()
            edit_page.wait_for_page_loaded()
        sub_measure()

        edit_page.write_content()

        @print_timing("selenium_edit_custom_page:save_edited_page")
        def sub_measure():
            edit_page.save_edited_page()
        sub_measure()
    measure()