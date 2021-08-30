from selenium.webdriver.common.by import By
from util.conf import BAMBOO_SETTINGS


class UrlManager:

    def __init__(self, page_id=None):
        self.host = BAMBOO_SETTINGS.server_url
        self.login_params = '/userlogin!doDefault.action?os_destination=%2FallPlans.action'
        self.logout_params = '/userLogout.action'

    def login_url(self):
        return f"{self.host}{self.login_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"


class LoginPageLocators:

    login_page_url = UrlManager().login_url()
    login_button = (By.ID, "loginForm_save")
    login_username_field = (By.ID, "loginForm_os_username")
    login_password_field = (By.ID, "loginForm_os_password")


class LogoutLocators:
    logout = (By.XPATH, "//a[@href='/userLogout.action']")

