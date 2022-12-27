import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login
from util.conf import JIRA_SETTINGS


def app_single_action(webdriver, datasets):
    issue_page = Issue(webdriver, issue_key=datasets['issue_key'])

    @print_timing("selenium_xporter_single_export_dialog")
    def selenium_xporter_single_export_dialog():
        @print_timing("selenium_app_custom_action:selenium_xporter_single_export_dialog")

        def measure():
            issue_page.go_to()
            issue_page.wait_for_page_loaded()
        measure()

        def sub_measure():
            #wait for the Export button on Issue Detail
            issue_page.wait_until_visible((By.XPATH, "//span[@class='dropdown-text'][text()='Export']")).click()

            #wait and click on Xporter button
            issue_page.wait_until_visible((By.ID, 'com.xpandit.plugins.jiraxporter:single-issue-export')).click()

            #wait and click in order to start the export.
            issue_page.wait_until_visible((By.ID, "xporter-general-export")).click()
            issue_page.wait_until_visible((By.XPATH, "//strong[text()='Success!']"))
        sub_measure()
    selenium_xporter_single_export_dialog()

def app_bulk_action(webdriver, datasets):
    custom_jql = urllib.parse.quote(random.choice(datasets['custom_jqls'][0]))
    search_page = Search(webdriver, jql=custom_jql)
    @print_timing("selenium_xporter_bulk_export_dialog")

    def selenium_xporter_bulk_export_dialog():

        @print_timing("selenium_search_jql")
        def measure():
            search_page.go_to()
            search_page.wait_for_page_loaded()
        measure()

        def sub_measure():
            #wait for the Export button on Issue Detail
            search_page.wait_until_visible((By.XPATH, "//span[@class='aui-button-label'][text()='Export']")).click()

            #wait and click on Xporter button
            search_page.wait_until_visible((By.XPATH, "//a[@class='aui-list-item-link'][text()='Xporter']")).click()
            try:
            #wait and click in order to start the export.
                search_page.wait_until_visible((By.ID, "xporter-general-export")).click()
                search_page.wait_until_visible((By.XPATH, "//strong[text()='Success!']"))

            except:
                search_page.wait_until_visible((By.XPATH, "//strong[text()='Error!']"))
        sub_measure()
    selenium_xporter_bulk_export_dialog()

def app_xlsx_current_fields_action(webdriver, datasets):
    custom_jql = urllib.parse.quote(random.choice(datasets['custom_jqls'][0]))
    search_page = Search(webdriver, jql=custom_jql)
    @print_timing("selenium_xporter_xlsx_current_fields_export_dialog")

    def selenium_xlsx_current_fields_action():

        @print_timing("selenium_search_jql")
        def measure():
            search_page.go_to()
            search_page.wait_for_page_loaded()
        measure()

        def sub_measure():
            #wait for the Export button on Issue Detail
            search_page.wait_until_visible((By.XPATH, "//span[@class='aui-button-label'][text()='Export']")).click()

            #wait and click on Xporter button
            search_page.wait_until_visible((By.XPATH, "//a[@class='aui-list-item-link'][text()='XLSX (Current fields)']")).click()
        sub_measure()
    selenium_xlsx_current_fields_action()