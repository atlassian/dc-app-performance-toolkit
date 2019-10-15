from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from selenium_ui.conftest import print_timing, application_url
from util.project_paths import CONFLUENCE_YML

APPLICATION_URL = application_url(CONFLUENCE_YML)
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
