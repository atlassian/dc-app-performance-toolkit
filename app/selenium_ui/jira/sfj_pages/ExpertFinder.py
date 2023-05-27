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


class ExpertFinder(BasePage):
    def __init__(self, driver):
        BasePage.__init__(self, driver)

        self.urls = {
            "entry": "/plugins/servlet/skillsforjira/team#expertfinder"
        }
        self.selectors = {
            "controls": ".expert-finder .controls",
            "select-selected-nodes": ".expert-finder .controls *[class*=-control] > *",
            "node": '.expert-finder .rstcustom__rowWrapper'
        }

    def open_expert_finder(self):
        self.go_to_url(f'{JIRA_SETTINGS.server_url}{self.urls["entry"]}')
        
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['controls']),
        ])
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['node'])
        ])
        
    def click_expert_finder_node(self):
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['node'])) \
            .click()

        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['select-selected-nodes'])
        ])
        


