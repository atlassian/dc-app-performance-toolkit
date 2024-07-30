import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login
from util.conf import JIRA_SETTINGS

from selenium_ui.jira.pages.pages import Issue


class AppLocators:

    # default History panel
    tabpanel_changehistory = (By.ID, "changehistory-tabpanel")
    tabpanel_changehistory_contents = (By.CSS_SELECTOR, ".actionContainer :not(#issuecreateddetails-10000).action-details")
    tabpanel_changehistory_contents_users = (By.CSS_SELECTOR, ".actionContainer :not(#issuecreateddetails-10000).action-details a.user-avatar")

    # Issue History tracker
    tabpanel = (By.ID, "issue-history-tracker")
    select_result = (By.CLASS_NAME, "select2-results")
    select_result_item = (By.CSS_SELECTOR, ".select2-results .select2-result")
    select_result_item_first = (By.CSS_SELECTOR, ".select2-results li.select2-result:nth-child(1)")
    search_user = (By.CSS_SELECTOR, "#s2id_issue-tab-panel-user-selector")
    search_user_arrow_btton = (By.CSS_SELECTOR, "#s2id_issue-tab-panel-user-selector .select2-choices .select2-search-field")
    search_field = (By.ID, "s2id_issue-tab-panel-field-selector")
    reset_button = (By.ID, "reset-button")
    result_table = (By.ID, "issue-tab-panel-result-table")
    result_table_contents = (By.CSS_SELECTOR, "#issue-tab-panel-result-table > tbody > tr")
    result_table_contents_users = (By.CSS_SELECTOR, "#issue-tab-panel-result-table > tbody > tr > td[headers='updated-user']")
    search_user_selected = (By.CSS_SELECTOR, "#s2id_issue-tab-panel-user-selector .select2-choices .select2-search-choice")
    search_field_selected = (By.CSS_SELECTOR, "#s2id_issue-tab-panel-field-selector > a.select2-choice .select2-chosen")
    

def app_specific_action(webdriver, datasets):
    
    page = BasePage(webdriver)
    if datasets['custom_issues']:
        issue_page = Issue(
            webdriver,
            issue_key=datasets['custom_issue_key'])
    else:
        issue_page = Issue(
            webdriver,
            issue_key=datasets['current_session']['issue_key'])

    @print_timing("selenium_app_custom_action")
    def measure():
        @print_timing("view_issue-history-tracker")
        def sub_measure():
            issue_page.go_to()
            issue_page.wait_for_page_loaded()
            # issue_page.scroll_down_till_bottom()
            # issue_page.wait_until_present(AppLocators.tabpanel)  # Wait for you app-specific UI element by ID selector
            # issue_page.wait_until_visible(AppLocators.tabpanel)  # Wait for you app-specific UI element by ID selector
            issue_page.wait_until_clickable(AppLocators.tabpanel).click()
            issue_page.wait_until_visible(AppLocators.search_user)
            issue_page.wait_until_visible(AppLocators.search_field)
            issue_page.wait_until_visible(AppLocators.reset_button)
            issue_page.wait_until_visible(AppLocators.result_table)
        sub_measure()


    measure()
