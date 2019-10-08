import random
import time
import urllib.parse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jira.selenium_ui.conftest import print_timing, AnyEc, application_url, generate_random_string

APPLICATION_URL = application_url()
timeout = 20


def custom_action(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/plugins/servlet/some-app/reporter')
            WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.ID, 'plugin-element')))
        measure(webdriver, 'selenium_app_custom_action:view_report')

        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/plugins/servlet/some-app/administration')
            WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.ID, 'plugin-dashboard')))
        measure(webdriver, 'selenium_app_custom_action:view_dashboard')
    measure(webdriver, 'selenium_app_custom_action')
