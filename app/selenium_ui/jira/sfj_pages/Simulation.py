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


class Simulation(BasePage):
    def __init__(self, driver):
        BasePage.__init__(self, driver)

        self.urls = {
            "entry": "/plugins/servlet/skillsforjira/team#simulation"
        }
        self.selectors = {
            "carousel": '.simulation .carousel',
            "open-dialog-button": '.simulation .button-section .start-button',
            "open-dialog-button-active": '.simulation .button-section .start-button button:not([disabled])',
            "filter-users-select": '.filter-users',
            "filter-users-menu-item": '.filter-users [class*="-menu"] *:first-child',
            "filter-queues-select": '.filter-queues',
            "filter-queues-menu-item": '.filter-queues [class*="-menu"] *:first-child',
            "run-simulation-button": '.filters-submit-button',
            "simulation-report": '.simulation-result .simulation-result-header'
        }

    def open_simulation(self):
        self.go_to_url(f'{JIRA_SETTINGS.server_url}{self.urls["entry"]}')

        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['open-dialog-button-active']),
        ])

    def run_simulation(self):
        # print(f'Hiding carousel...')
        # self.driver.execute_script("document.getElementsByClassName('carousel')[0].style='display: none;'")
        # self.driver.execute_script("document.getElementsById('footer').style='display: none;'")
        
        print(f'Waiting until Open Dialog button is clickable...')
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['open-dialog-button-active']));
        #     .click()
        self.driver.execute_script(f"document.querySelector('{self.selectors['open-dialog-button-active']}').click()")
        
        print(f'Selecting 1 user...')
        # Select 1 user (for performance)
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['filter-users-select'])) \
            .click()
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['filter-users-menu-item']))\
            .click()
        
        print(f'Selecting 1 queue...')
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['filter-queues-select'])) \
            .click()
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['filter-queues-menu-item']))\
            .click()
        
        print(f'Running simulation...')
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['run-simulation-button'])) \
            .click()

        print(f'Waiting until simulation is complete and report genrated...')
        self.wait_until_any_ec_presented(selectors=[
            (By.CSS_SELECTOR, self.selectors['simulation-report'])
        ])