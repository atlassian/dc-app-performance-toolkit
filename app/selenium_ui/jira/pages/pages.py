from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.jira.pages.selectors import UrlManager, LoginPageLocators, DashboardLocators, PopupLocators


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.default_popup, PopupLocators.popup_1, PopupLocators.popup_2)


class LoginPage(BasePage):
    page_url = LoginPageLocators.login_url

    def at(self):
        return self.verify_url(LoginPageLocators.login_params)

    def is_first_login(self):
        return True if self.get_elements(LoginPageLocators.continue_button) else False

    def first_login_setup(self, interaction):
        self.wait_until_visible(LoginPageLocators.continue_button, interaction).send_keys(Keys.ESCAPE)
        self.get_element(LoginPageLocators.continue_button).click()
        self.wait_until_visible(LoginPageLocators.avatar_page_next_button, interaction).click()
        self.wait_until_visible(LoginPageLocators.explore_current_projects, interaction).click()
        self.go_to_url(DashboardLocators.dashboard_url)
        self.wait_until_visible(DashboardLocators.dashboard_window, interaction)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()


class Issue(BasePage):

    def __init__(self, driver, issue):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(issue=issue)
        self.page_url = url_manager.issue_url()
        self.params_to_verify = url_manager.issue_params

    def at(self):
        return self.verify_url(self.params_to_verify)
