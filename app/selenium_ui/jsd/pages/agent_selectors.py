from util.conf import JSD_SETTINGS
from selenium.webdriver.common.by import By


class PopupLocators:
    default_popup = '.aui-message .icon-close'
    popup_1 = 'form.tip-footer>.helptip-close'
    popup_2 = '.aui-inline-dialog-contents .cancel'


class UrlManager:

    def __init__(self, project_key=None, request_key=None):
        self.host = JSD_SETTINGS.server_url
        self.login_params = '/login.jsp'
        self.logout_params = '/logoutconfirm.jsp'
        self.dashboard_params = '/secure/Dashboard.jspa'
        self.browse_all_projects = '/secure/BrowseProjects.jspa'
        self.browse_project_customers = f'/projects/{project_key}/customers'
        self.view_customer_request = f'/browse/{request_key}'

    def login_url(self):
        return f'{self.host}{self.login_params}'

    def dashboard_url(self):
        return f"{self.host}{self.dashboard_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"

    def browse_all_projects_url(self):
        return f'{self.host}{self.browse_all_projects}'

    def browse_project_customers_page_url(self):
        return f"{self.host}{self.browse_project_customers}"

    def view_customer_request_url(self):
        return f'{self.host}{self.view_customer_request}'


class LoginPageLocators:

    login_url = UrlManager().login_url()

    # First time login setup page
    continue_button = (By.ID, 'next')
    avatar_page_next_button = (By.CSS_SELECTOR, "input[value='Next']")
    explore_current_projects = (By.CSS_SELECTOR, "a[data-step-key='browseprojects']")
    login_field = (By.ID, 'login-form-username')
    password_field = (By.ID, 'login-form-password')
    login_submit_button = (By.ID, 'login-form-submit')
    system_dashboard = (By.ID, "dashboard")


class DashboardLocators:

    dashboard_url = UrlManager().dashboard_url()
    dashboard_params = UrlManager().dashboard_params
    dashboard_window = (By.CLASS_NAME, "page-type-dashboard")


class LogoutLocators:

    logout_url = UrlManager().logout_url()
    logout_submit_button = (By.ID, "confirm-logout-submit")
    login_button_link = (By.CLASS_NAME, "login-link")


class BrowseProjectsLocators:

    brows_projects_url = UrlManager().browse_all_projects_url()
    page_title = (By.XPATH, "//h1[contains(text(),'Browse projects')]")


class BrowseCustomersLocators:

    page_title = (By.XPATH, "//h2[contains(text(),'Customers')]")


class ViewCustomerRequestLocators:

    bread_crumbs = (By.CSS_SELECTOR, ".aui-nav.aui-nav-breadcrumbs")

    comment_collapsed_textarea = (By.ID, "sd-comment-collapsed-textarea")
    comment_text_field_RTE = (By.XPATH, "//div[textarea[@id='comment']]//iframe")
    comment_text_field = (By.XPATH, "//textarea[@id='comment']")
    comment_tinymce_field = (By.ID, "tinymce")
    comment_internally_btn = (By.XPATH, "//button[contains(text(),'Comment internally')]")
