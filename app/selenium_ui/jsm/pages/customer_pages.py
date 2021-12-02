import random
from datetime import datetime

from packaging import version
from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.jsm.pages.customer_selectors import UrlManager, LoginPageLocators, TopPanelSelectors, \
    CustomerPortalsSelectors, CustomerPortalSelectors, RequestSelectors, RequestsSelectors


class Login(BasePage):
    page_url = LoginPageLocators.login_url
    page_loaded_selector = LoginPageLocators.login_submit_button

    def set_credentials(self, username, password):
        self.wait_until_visible(LoginPageLocators.login_field)
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()

    def is_logged_in(self):
        elements = self.get_elements(CustomerPortalsSelectors.welcome_logged_in_page)
        return True if elements else False

    def get_app_version(self):
        version_str = self.get_element(LoginPageLocators.app_version).get_attribute('content')
        return version.parse(version_str)


class TopPanel(BasePage):

    def open_profile_menu(self):
        self.get_element(TopPanelSelectors.profile_icon).click()
        self.wait_until_visible(TopPanelSelectors.logout_button)

    def logout(self):
        self.get_element(TopPanelSelectors.logout_button).click()
        self.wait_until_invisible(TopPanelSelectors.profile_icon)


class CustomerPortals(BasePage):
    page_loaded_selector = CustomerPortalsSelectors.welcome_logged_in_page

    def browse_projects(self):
        self.wait_until_visible(CustomerPortalsSelectors.browse_portals_button)
        self.get_element(CustomerPortalsSelectors.browse_portals_button).click()
        self.wait_until_visible(self.get_selector(CustomerPortalsSelectors.full_portals_list))

    def open_random_portal(self):
        portals = self.get_elements(CustomerPortalsSelectors.portal_from_list)
        if len(portals) > 1:
            portal = random.choice(portals)
        else:
            portal = portals[0]
        portal.click()


class CustomerPortal(BasePage):
    page_loaded_selector = CustomerPortalSelectors.portal_title
    timeout = 30

    def __init__(self, driver, portal_id):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(portal_id=portal_id)
        self.page_url = url_manager.portal_url()

    def chose_random_request_type(self):
        request_types = self.get_elements(CustomerPortalSelectors.request_type)
        if len(request_types) > 1:
            request_type = random.choice(request_types)
        else:
            request_type = request_types[0]
        request_type.click()
        self.wait_until_visible(CustomerPortalSelectors.create_request_button)

    def create_and_submit_request(self):
        self.get_element(CustomerPortalSelectors.summary_field).\
            send_keys(f'Selenium - {self.generate_random_string(5)}')
        selector = self.get_selector(CustomerPortalSelectors.description_field)
        self.wait_until_visible(selector).send_keys(f'Selenium - Description {self.generate_random_string(5)}')

        # If required dropdown
        required_dropdown_elements = self.get_elements(CustomerPortalSelectors.required_dropdown_field)
        if required_dropdown_elements:
            dropdown = required_dropdown_elements[0]
            dropdown.click()
            self.wait_until_visible(CustomerPortalSelectors.required_dropdown_list)
            self.wait_until_visible(CustomerPortalSelectors.required_dropdown_element)
            self.action_chains().move_to_element(
                random.choice(self.get_elements(CustomerPortalSelectors.required_dropdown_element))).click().perform()
            self.wait_until_invisible(CustomerPortalSelectors.required_dropdown_list)

        required_calendar_field = self.get_elements(CustomerPortalSelectors.required_calendar_button)
        if required_calendar_field:
            date_now = f"{datetime.now().day}/{datetime.now().strftime('%h')}/{datetime.now().strftime('%Y')}"
            self.wait_until_visible(CustomerPortalSelectors.required_calendar_input_field)
            self.get_element(CustomerPortalSelectors.required_calendar_input_field).send_keys(date_now)

        self.get_element(CustomerPortalSelectors.create_request_button).click()
        self.wait_until_visible(self.get_selector(RequestSelectors.comment_request_field))


class CustomerRequest(BasePage):

    def __init__(self, driver, portal_id, request_key):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(portal_id=portal_id, request_key=request_key)
        self.page_url = url_manager.request_url()

    page_loaded_selector = RequestSelectors.request_option

    def comment_request(self):
        self.wait_until_visible(self.get_selector(RequestSelectors.comment_field_minimized)).click()
        self.wait_until_visible(self.get_selector(RequestSelectors.comment_request_field)).\
            send_keys(f'Selenium comment - {self.generate_random_string(10)}')
        self.wait_until_clickable(RequestSelectors.add_comment_button)
        self.get_element(RequestSelectors.add_comment_button).click()
        self.wait_until_invisible(RequestSelectors.add_comment_button)

    def search_for_customer_to_share_with(self, customer_name):
        if not self.element_exists(RequestSelectors.share_request_button):
            print(f'Request {self.page_url} does not have Share button')
            return

        self.wait_until_visible(RequestSelectors.share_request_button).click()
        self.wait_until_visible(RequestSelectors.share_request_search_field).click()

        self.action_chains().move_to_element(self.get_element(RequestSelectors.share_request_search_field)).\
            send_keys(customer_name).perform()
        self.wait_until_visible(RequestSelectors.share_request_dropdown)

        # Chose random customer to share with
        self.wait_until_visible(RequestSelectors.share_request_dropdown_one_elem)

        random_customer_name = random.choice([i.text for i in
                                              self.get_elements(RequestSelectors.share_request_dropdown_one_elem)])
        self.action_chains().move_to_element(
            self.get_element(RequestSelectors.share_request_search_field)).click().perform()

        self.wait_until_invisible(RequestSelectors.share_request_dropdown)

        self.action_chains().move_to_element(self.get_element(RequestSelectors.share_request_search_field)).send_keys(
            random_customer_name).perform()

        self.wait_until_visible(RequestSelectors.share_request_dropdown_one_elem)
        self.action_chains().move_to_element(self.get_element(RequestSelectors.share_request_search_field)).send_keys(
            Keys.RETURN).perform()

        self.wait_until_invisible(RequestSelectors.share_request_dropdown)

    def share_request(self):
        self.wait_until_visible(RequestSelectors.share_request_modal_button).click()
        self.wait_until_invisible(RequestSelectors.share_request_modal_button)


class Requests(BasePage):

    def __init__(self, driver, all_requests=False):
        BasePage.__init__(self, driver)
        url_manager = UrlManager()
        self.page_url = url_manager.all_requests_url() if all_requests else url_manager.my_requests_url()

    page_loaded_selector = RequestsSelectors.requests_label
