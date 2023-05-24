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


class AssignmentsDashboard(BasePage):
    def __init__(self, driver):
        BasePage.__init__(self, driver)

        self.urls = {
            "entry": "/plugins/servlet/skillsforjira/team#assignments"
        }
        self.selectors = {
            "in_progress_widget_loaded": '.in-progress-widget .issues-list:not(.blurred), .in-progress-widget h4',
            "queue_widget_loaded": '.queue-widget .issues-list:not(.blurred), .queue-widget h4',
            "demand_widget_loaded": '.skills-demand-widget div:nth-child(3):not(.blurred), .skills-demand-widget h4',
            "pull_widget_loaded": ".pull-widget:not(.blurred)",
            "pull-button": '.pull-widget button',
            "pull-button-inactive": '.pull-widget button[disabled]',
            "pull-button-active": '.pull-widget button:not([disabled])',
            "pull-success-message": '.pull-widget .notification *[style*="success"]',
            "pull-error-message": '.pull-widget .notification *[style*="danger"]',
        }

    def open_assignments_dashboard(self):
        self.go_to_url(f'{JIRA_SETTINGS.server_url}{self.urls["entry"]}')
        
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['pull_widget_loaded']),
        ])
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['in_progress_widget_loaded'])
        ])
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['queue_widget_loaded'])
        ])
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['demand_widget_loaded'])
        ])

    def pull_assignment(self):
        # self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['pull-button'])) # Doesn't work for some reason
        # self.wait_until_visible((By.CSS_SELECTOR, self.selectors['pull-button-active'])) \
        #     .click()

        self.driver.execute_script(f"document.querySelector('{self.selectors['pull-button-active']}').click()")

        # self.wait_until_visible((By.CSS_SELECTOR, self.selectors['pull-button-inactive']))
        
        self.wait_until_visible((By.CSS_SELECTOR, self.selectors['pull-success-message']))

