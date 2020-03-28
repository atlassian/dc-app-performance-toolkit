from selenium.webdriver.common.by import By
from util.conf import JIRA_SETTINGS


class PopupLocators:
    default_popup = '.aui-message .icon-close'
    popup_1 = 'form.tip-footer>.helptip-close'
    popup_2 = '.aui-inline-dialog-contents .cancel'


class UrlManager:

    def __init__(self, issue=None):
        self.host = JIRA_SETTINGS.server_url
        self.login_params = '/login.jsp'
        self.dashboard_params = '/secure/Dashboard.jspa'
        self.issue_params = f"/browse/{issue}"

    def login_url(self):
        return f"{self.host}{self.login_params}"

    def dashboard_url(self):
        return f"{self.host}{self.dashboard_params}"

    def issue_url(self):
        return f"{self.host}{self.issue_params}"


class LoginPageLocators:

    login_url = UrlManager().login_url()
    login_params = UrlManager().login_params

    # First time login setup page
    continue_button = (By.ID, 'next')
    avatar_page_next_button = (By.CSS_SELECTOR, "input[value='Next']")
    explore_current_projects = (By.CSS_SELECTOR, "a[data-step-key='browseprojects']")
    login_field = (By.ID, 'login-form-username')
    password_field = (By.ID, 'login-form-password')
    login_submit_button = (By.ID, 'login-form-submit')

class DashboardLocators:

    dashboard_url = UrlManager().dashboard_url()
    dashboard_params = UrlManager().dashboard_params
    dashboard_window = (By.CLASS_NAME, "page-type-dashboard")
