from collections import OrderedDict

from selenium.webdriver.common.by import By

from util.conf import JSM_SETTINGS


class UrlManager:

    def __init__(self, portal_id=None, request_key=None):
        self.host = JSM_SETTINGS.server_url
        self.login_params = '/servicedesk/customer/user/login'
        self.portal_params = f'/servicedesk/customer/portal/{portal_id}'
        self.request_params = f'/servicedesk/customer/portal/{portal_id}/{request_key}'
        self.my_requests = '/servicedesk/customer/user/requests'
        self.all_requests = '/servicedesk/customer/user/requests?reporter=all'

    def login_url(self):
        return f'{self.host}{self.login_params}'

    def portal_url(self):
        return f'{self.host}{self.portal_params}'

    def request_url(self):
        return f'{self.host}{self.request_params}'

    def my_requests_url(self):
        return f'{self.host}{self.my_requests}'

    def all_requests_url(self):
        return f'{self.host}{self.all_requests}'


class LoginPageLocators:
    login_url = UrlManager().login_url()

    search_input_field = (By.ID, 'sd-customer-portal-smart-search-input')
    login_field = (By.ID, 'os_username')
    password_field = (By.ID, 'os_password')
    login_submit_button = (By.ID, 'js-login-submit')
    app_version = (By.NAME, "ajs-sdPluginVersion")


class TopPanelSelectors:
    profile_icon = (By.XPATH, '//a[@href="#dropdown2-header"]')
    profile_button = (By.CSS_SELECTOR, 'a.js-profile')
    logout_button = (By.CSS_SELECTOR, 'a.js-logout')


class CustomerPortalsSelectors:
    welcome_logged_in_page = (By.CSS_SELECTOR, "div.cv-help-center-container")
    browse_portals_button = (By.CSS_SELECTOR, "button.cv-smart-portal-browse-portals")
    full_portals_list = OrderedDict({"4.13.0": (By.CSS_SELECTOR, "ul.cv-smart-portal-all-portals-list"),
                                     "4.15.0": (By.CLASS_NAME, "cv-portal-cards-react-container")})
    portal_from_list = OrderedDict({"4.13.0": (By.CSS_SELECTOR, "ul.cv-smart-portal-all-portals-list>li>a>span"),
                                    "4.15.0": (By.CSS_SELECTOR, "portal-card-item")})


class CustomerPortalSelectors:
    portal_title = (By.CSS_SELECTOR, '.cv-page-title-text')
    request_type = (By.CSS_SELECTOR, 'li>span.js-cv-request-type>a')
    create_request_button = (By.XPATH, "//button[contains(text(),'Create')]")
    summary_field = (By.ID, 'summary')
    description_field = OrderedDict({"4.13.0": (By.ID, 'description'),
                                     "4.15.0": (By.CLASS_NAME, "ProseMirror")})
    required_dropdown_field = (By.CSS_SELECTOR, "#s2id_components>ul.select2-choices")
    required_dropdown_list = (By.ID, 'select2-drop')
    required_dropdown_element = (By.CSS_SELECTOR, '#select2-drop>ul.select2-results>li')

    required_calendar_button = (By.CSS_SELECTOR, 'button#trigger-duedate')
    required_calendar_input_field = (By.CSS_SELECTOR, 'input#duedate')


class RequestSelectors:
    request_url = UrlManager().request_url()
    request_option = (By.CLASS_NAME, 'cv-request-options')
    comment_field_minimized = OrderedDict({"4.13.0": (By.CSS_SELECTOR, 'textarea#comment-on-request'),
                                           "4.15.0": (By.CLASS_NAME, 'cv-request-comment')})
    comment_request_field = OrderedDict({"4.13.0": (By.CSS_SELECTOR, 'textarea#comment-on-request'),
                                         "4.15.0": (By.CLASS_NAME, 'ProseMirror')})
    add_comment_button = (By.XPATH, "//button[contains(text(),'Add')]")
    share_request_button = (By.CSS_SELECTOR, 'a.js-share-request')
    share_request_search_field = (By.ID, 's2id_participants')
    share_request_dropdown = (By.ID, 'select2-drop')
    share_request_dropdown_results = (By.CSS_SELECTOR, '#select2-drop>ul.select2-results>li')
    share_request_dropdown_one_elem = (By.CSS_SELECTOR,
                                       '#select2-drop>ul.select2-results>li>div>span.user-picker-display-name')

    share_request_modal_button = (By.XPATH, "//button[contains(text(),'Share')]")
    list_of_requests_types = (By.ID, "cv-request-content")


class InsightSelectors:
    insight_field_icon = (By.CLASS_NAME, "js-rlabs-sd-customfield-object-picker")


class RequestsSelectors:
    my_requests_url = UrlManager().my_requests_url()
    requests_label = (By.XPATH, "//h2[contains(text(),'Requests')]")
