from selenium_ui.base_page import BasePage

from selenium_ui.bamboo.pages.selectors import UrlManager, LoginPageLocators, LogoutLocators


class Login(BasePage):
    page_url = LoginPageLocators.login_page_url

    def click_login_button(self):
        self.wait_until_visible(LoginPageLocators.login_button).click()
        self.wait_until_invisible(LoginPageLocators.login_button)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_username_field).send_keys(username)
        self.get_element(LoginPageLocators.login_password_field).send_keys(password)


class Logout(BasePage):
    page_url = UrlManager().logout_url()
    logout = LogoutLocators.logout





