import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login
from util.conf import JIRA_SETTINGS
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    if datasets['custom_issues']:
        issue_key = datasets['custom_issue_key']

  # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action
    #
    @print_timing("selenium_app_specific_user_login")
    def measure():
        def app_specific_user_login(username='admin', password='admin'):
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.set_credentials(username=username, password=password)
#            if login_page.is_first_login():
#                login_page.first_login_setup()
#            if login_page.is_first_login_second_page():
#                login_page.first_login_second_page_setup()
#            login_page.wait_for_page_loaded()
        app_specific_user_login(username='admin', password='admin')
        print("logging in using app specific user login")
    measure()



#    @print_timing("selenium_app_custom_action")
#    def measure():
#        @print_timing("selenium_app_custom_action:view_issue")
#        def sub_measure():
#            page.go_to_url(f"{JIRA_SETTINGS.server_url}/browse/{issue_key}")
#            page.wait_until_visible((By.ID, "summary-val"))  # Wait for summary field visible
#            page.wait_until_visible((By.ID, "ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT"))  # Wait for you app-specific UI element by ID selector
#        sub_measure()
    measure()

def navigate_to_test_suite_page(webdriver, datasets):
    @print_timing("navigate_to_test_suite_page")
    def measure():
#        testSuite_page = TestSuite(webdriver)
#        synapsert_Tests = (By.ID, "synapse-link-synapsert")
        @print_timing("selenium_app_custom_action:testSuitePage")
        def sub_measure():
             webdriver.find_element_by_id("synapse-link-synapsert").click()
             webdriver.find_element_by_id("com.go2group.jira.plugin.synapse:synapse-test-suites-link_lnk").click()
             webdriver.find_element_by_id("activeTabMessageDiv").is_displayed()
        sub_measure()
    measure()

def navigate_to_traceability_report_page(webdriver):
    @print_timing("navigate_to_traceability_report_page")
    def measure():
        @print_timing("selenium_app_custom_action:app_traceability_page")
        def sub_measure():
             webdriver.find_element_by_id("synapse-link-synapsert").click()
             webdriver.find_element_by_id("com.go2group.jira.plugin.synapse:synapse-traceability-link_lnk").click()
             webdriver.find_element_by_id("s2id_reqProject").is_displayed()
        sub_measure()
    measure()

def navigate_to_app_report_page(webdriver):
    @print_timing("navigate_to_app_report_page")
    def measure():
        @print_timing("selenium_app_custom_action:app report page")
        def sub_measure():
             webdriver.find_element_by_id("synapse-link-synapsert").click()
             webdriver.find_element_by_id("com.go2group.jira.plugin.synapse:synapse-reports-link_lnk").click()
             element = WebDriverWait(webdriver, 10).until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'SynapseRT Reports')]")))
             webdriver.find_element_by_xpath("//h1[contains(text(),'SynapseRT Reports')]").is_displayed()
        sub_measure()
    measure()

def navigate_to_my_settings_page(webdriver):
    @print_timing("navigate_to_my_settings_page")
    def measure():
        @print_timing("selenium_app_custom_action:my settings page")
        def sub_measure():
             webdriver.find_element_by_id("synapse-link-synapsert").click()
             webdriver.find_element_by_id("synapse-link-subscription_lnk").click()
             webdriver.find_element_by_xpath("//a[contains(text(),'Preferences')]").is_displayed()
        sub_measure()
    measure()

