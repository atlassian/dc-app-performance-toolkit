import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bitbucket.pages.pages import LoginPage, GetStarted, AdminPage, PopupManager
from util.conf import BITBUCKET_SETTINGS


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    rnd_repo = random.choice(datasets["repos"])

    project_key = rnd_repo[1]
    repo_slug = rnd_repo[0]

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_logout action

    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = LoginPage(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.wait_for_page_loaded()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.submit_login()
    #         get_started_page = GetStarted(webdriver)
    #         get_started_page.wait_for_page_loaded()
    #         PopupManager(webdriver).dismiss_default_popup()
    #         get_started_page.close_whats_new_window()
    #
    #         # uncomment below line to do web_sudo and authorise access to admin pages
    #         # AdminPage(webdriver).go_to(password=password)
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_custom_action")
    def measure():

        @print_timing("selenium_app_custom_action:view_repo_page")
        def sub_measure():
            page.go_to_url(f"{BITBUCKET_SETTINGS.server_url}/projects/{project_key}/repos/{repo_slug}/browse")
            page.wait_until_visible((By.CSS_SELECTOR, '.aui-navgroup-vertical>.aui-navgroup-inner')) # Wait for repo navigation panel is visible
            page.wait_until_visible((By.ID, 'ID_OF_YOUR_APP_SPECIFIC_UI_ELEMENT'))  # Wait for you app-specific UI element by ID selector
        sub_measure()
    measure()
