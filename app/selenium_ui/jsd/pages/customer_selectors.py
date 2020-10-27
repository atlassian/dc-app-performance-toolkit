from util.conf import JSD_SETTINGS
from selenium.webdriver.common.by import By


class UrlManager:

    def __init__(self):
        self.host = JSD_SETTINGS.server_url
        self.login_params = '/servicedesk/customer/user/login'
        self.customer_portals_params = '/servicedesk/customer/portals'

    def login_url(self):
        return f'{self.host}{self.login_params}'

    def customer_portals_url(self):
        return f'{self.host}{self.customer_portals_params}'


class LoginPageLocators:
    login_url = UrlManager().login_url()

    search_input_field = (By.ID, 'sd-customer-portal-smart-search-input')
    login_field = (By.ID, 'os_username')
    password_field = (By.ID, 'os_password')
    login_submit_button = (By.ID, 'js-login-submit')


class CustomerPortalsPageLocators:
    customer_portals_url = UrlManager().customer_portals_url()
    search_input_field = (By.ID, 'sd-customer-portal-smart-search-input')


class TopPanelSelector:

    profile_icon = (By.CLASS_NAME, 'cp-avatar-image')
    profile_button = (By.CSS_SELECTOR, 'a.js-profile')
    logout_button = (By.CSS_SELECTOR, 'a.js-logout')






