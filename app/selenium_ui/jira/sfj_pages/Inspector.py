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


class Inspector(BasePage):
    def __init__(self, driver):
        BasePage.__init__(self, driver)

        self.urls = {
            "entry": "/plugins/servlet/skillsforjira/team#inspector"
        }
        self.selectors = {
            "user-selector": ".inspector [class*='-control']",
            "user-selector-menu": ".inspector [class*='-menu']",
            "user-selector-menu-item": ".inspector [class*='-menu'] *:first-child",
            
            "in_progress_widget_loaded": '.in-progress-widget .issues-list:not(.blurred), .in-progress-widget h4',
            "queue_widget_loaded": '.queue-widget .issues-list:not(.blurred), .queue-widget h4',
            "demand_widget_loaded": '.skills-demand-widget div:nth-child(3):not(.blurred), .skills-demand-widget h4',
        }

    def open_inspector(self):
        self.go_to_url(f'{JIRA_SETTINGS.server_url}{self.urls["entry"]}')

        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['user-selector']),
        ])
        
    def select_user(self):
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['user-selector'])).click()

        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['user-selector-menu']),
        ])
        
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['user-selector-menu-item'])).click()

        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['in_progress_widget_loaded'])
        ])
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['queue_widget_loaded'])
        ])
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['demand_widget_loaded'])
        ])