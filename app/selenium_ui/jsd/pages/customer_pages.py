from selenium_ui.base_page import BasePage

from selenium_ui.jsd.pages.customer_selectors import UrlManager, LoginPageLocators, CustomerPortalsPageLocators, \
    TopPanelSelector


class Login(BasePage):
    page_url = LoginPageLocators.login_url
    page_loaded_selector = LoginPageLocators.search_input_field

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()


class CustomerPortals(BasePage):
    page_url = CustomerPortalsPageLocators.customer_portals_url
    page_loaded_selector = CustomerPortalsPageLocators.search_input_field


class TopPanel(BasePage):

    def open_profile_menu(self):
        self.get_element(TopPanelSelector.profile_icon).click()
        self.wait_until_visible(TopPanelSelector.logout_button)

    def logout(self):
        self.get_element(TopPanelSelector.logout_button).click()
        self.wait_until_invisible(TopPanelSelector.profile_icon)


