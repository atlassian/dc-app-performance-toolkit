import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.bamboo.pages.pages import Login
from util.conf import BAMBOO_SETTINGS
from selenium_ui.bamboo.pages.pages import BuildSummary


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    rnd_plan = random.choice(datasets["build_plans"])

    build_plan_id = rnd_plan[1]

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action
    #
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.set_credentials(username=username, password=password)
    #         login_page.click_login_button()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    @print_timing("selenium_app_specific_view_summary_page")
    def measure():
        build_summary = BuildSummary(webdriver, build_plan_id=datasets['build_plan_id'])
        build_summary.go_to_build_summary_page()
        build_summary.wait_for_page_loaded()
        build_summary.wait_until_visible((By.CLASS_NAME, "clm-scan"))
    measure()

