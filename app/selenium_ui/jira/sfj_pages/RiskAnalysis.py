from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_ui.conftest import retry
import time
import random
import json
from util.conf import JIRA_SETTINGS

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Issue

from selenium_ui.jira.pages.selectors import UrlManager, LoginPageLocators, LogoutLocators


class RiskAnalysis(BasePage):
    def __init__(self, driver, project_key=None):
        BasePage.__init__(self, driver)

        self.project_key = project_key
        
        self.urls = {
            "entry": "/plugins/servlet/skillsforjira/team#riskanalysis"
        }
        self.selectors = {
            "search-input": ".risk-analysis input[type=search]",
            "filters": ".risk-analysis .filters",
            "filter": ".risk-analysis .filters .item:first-child",
            "usergroup-selector": ".risk-analysis .filter-users > div",
            "submit-button": ".risk-analysis .search-box button",
            "report": ".risk-analysis .report"
        }

    def open_risk_analysis(self):
        self.go_to_url(f'{JIRA_SETTINGS.server_url}{self.urls["entry"]}')

        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['search-input']),
        ])

    def run_risk_analysis(self):
        self.get_element((By.CSS_SELECTOR, self.selectors['search-input']))\
            .send_keys("project={}".format(self.project_key))
        
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['submit-button'])) \
            .click()
        
        # self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['filter'])) \
        #     .click()

        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['report'])
        ])