from selenium.webdriver.common.by import By
from selenium_ui.conftest import print_timing
from util.conf import BITBUCKET_SETTINGS

from selenium_ui.base_page import BasePage


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    repo = datasets['repos']
    repo_slug = repo[0]
    project_key = repo[1]

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:view_repo_page")
        def sub_measure():
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/projects/{project_key}/repos/{repo_slug}/browse")
            page.wait_until_visible((By.CSS_SELECTOR, '.aui-navgroup-vertical>.aui-navgroup-inner')) # Wait for repo navigation panel is visible
            page.wait_until_visible((By.ID, 'ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT'))  # Wait for you app-specific UI element by ID selector
        sub_measure()
    measure()
