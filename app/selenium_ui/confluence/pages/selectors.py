from selenium.webdriver.common.by import By
from util.conf import CONFLUENCE_SETTINGS


class UrlManager:

    def __init__(self, page_id=None):
        self.host = CONFLUENCE_SETTINGS.server_url
        self.login_params = '/login.action'
        self.page_params = f"/pages/viewpage.action?pageId={page_id}&noRedirect=true"
        self.dashboard_params = '/dashboard.action#all-updates'
        self.edit_page_params = f'/pages/editpage.action?pageId={page_id}'
        self.logout_params = "/logout.action"
        self.admin_system_params = f"/admin/viewgeneralconfig.action"

    def login_url(self):
        return f"{self.host}{self.login_params}"

    def dashboard_url(self):
        return f"{self.host}{self.dashboard_params}"

    def page_url(self):
        return f"{self.host}{self.page_params}"

    def edit_page_url(self):
        return f"{self.host}{self.edit_page_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"

    def admin_system_url(self):
        return f"{self.host}{self.admin_system_params}"


class PopupLocators:
    popup_selectors = [
        (By.CSS_SELECTOR, ".button-panel-button .set-timezone-button"),
        (By.CSS_SELECTOR, ".aui-button aui-button-link .skip-onboarding"),
        (By.CSS_SELECTOR, ".aui-button.aui-button-link.skip-onboarding"),
        (By.CSS_SELECTOR, "#closeDisDialog"),
        (By.CSS_SELECTOR, ".aui-button.aui-button-primary.show-onboarding"),
        (By.CSS_SELECTOR, 'button[aria-label="Close this modal"]')
    ]


class LoginPageLocators:

    sidebar = (By.ID, "sidebar-container")

    # legacy login form
    login_button = (By.ID, "loginButton")
    login_username_field = (By.ID, "os_username")
    login_password_field = (By.ID, "os_password")

    # 2sv login form
    login_button_2sv = (By.ID, "login-button")
    login_username_field_2sv = (By.ID, "username-field")
    login_password_field_2sv = (By.ID, "password-field")

    login_page_url = UrlManager().login_url()
    footer_build_info = (By.ID, "footer-build-information")
    footer_node_info = (By.ID, "footer-cluster-node")

    # Setup user page per first login
    first_login_setup_page = (By.ID, "grow-ic-nav-container")
    current_step_sel = (By.CLASS_NAME, "grow-aui-progress-tracker-step-current")
    skip_welcome_button = (By.ID, "grow-intro-video-skip-button")
    skip_photo_upload = (By.CSS_SELECTOR, ".aui-button-link")
    skip_find_content = (By.CSS_SELECTOR, ".intro-find-spaces-space>.space-checkbox")
    finish_setup = (By.CSS_SELECTOR, ".intro-find-spaces-button-continue")

    # logout
    logout = (By.XPATH, "//a[@href='logout.action']")


class AllUpdatesLocators:
    updates_content = (By.CLASS_NAME, "list-container-all-updates")


class PageLocators:
    page_title = (By.ID, "title-text")
    comment_text_field = (By.CSS_SELECTOR, ".quick-comment-prompt")
    edit_page_button = (By.ID, "editPageLink")
    search_box = (By.ID, "quick-search-query")
    search_results = (By.ID, "search-result-container")
    close_search_button = (By.ID, "search-drawer-close")
    empty_search_results = (By.CLASS_NAME, "captioned-image-component")


class DashboardLocators:
    dashboard_url = UrlManager().dashboard_url()
    all_updates = (By.CLASS_NAME, "content-header-all-updates")


class TopPanelLocators:
    create_button = (By.ID, "quick-create-page-button")


class EditorLocators:
    publish_button = (By.ID, "rte-button-publish")
    confirm_publishing_button = (By.ID, "qed-publish-button")
    title_field = (By.ID, "content-title")
    page_content_field = (By.ID, "wysiwygTextarea_ifr")
    tinymce_page_content_field = (By.ID, "tinymce")
    tinymce_page_content_parahraph = (By.TAG_NAME, 'p')

    status_indicator = (By.CLASS_NAME, "status-indicator-message")
    save_spinner = (By.ID, "rte-spinner")


class LogoutLocators:
    logout_msg = (By.ID, "logout-message")


class XsrfTokenLocators:
    xsrf_token = (By.ID, "atlassian-token")

class AdminLocators:
    admin_system_page_url = UrlManager().admin_system_url()
    web_sudo_password = (By.ID, 'password')
    web_sudo_submit_btn = (By.ID, 'authenticateButton')
    login_form = (By.ID, 'login-container')
    edit_baseurl = (By.ID, 'editbaseurl')
