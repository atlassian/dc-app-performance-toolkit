from selenium.webdriver.common.by import By
from util.conf import JIRA_SETTINGS


class PopupLocators:
    default_popup = '.aui-message .icon-close'
    popup_1 = 'form.tip-footer>.helptip-close'
    popup_2 = '.aui-inline-dialog-contents .cancel'


class UrlManager:

    def __init__(self, issue_key=None, issue_id=None, project_key=None, jql=None):
        self.host = JIRA_SETTINGS.server_url
        self.login_params = '/login.jsp'
        self.dashboard_params = '/secure/Dashboard.jspa'
        self.issue_params = f"/browse/{issue_key}"
        self.project_summary_params = f"/projects/{project_key}/summary"
        self.jql_params = f"/issues/?jql={jql}"
        self.edit_issue_params = f"/secure/EditIssue!default.jspa?id={issue_id}"

    def login_url(self):
        return f"{self.host}{self.login_params}"

    def dashboard_url(self):
        return f"{self.host}{self.dashboard_params}"

    def issue_url(self):
        return f"{self.host}{self.issue_params}"

    def project_summary_url(self):
        return f"{self.host}{self.project_summary_params}"

    def jql_search_url(self):
        return f"{self.host}{self.jql_params}"

    def edit_issue_url(self):
        return f"{self.host}{self.edit_issue_params}"


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


class IssueLocators:

    issue_title = (By.ID, "summary-val")

    create_issue_button = (By.ID, "create_link")
    # Issue create modal form
    issue_modal = (By.ID, "create-issue-dialog")
    issue_summary_field = (By.ID, "summary")
    issue_description_field = (By.XPATH, f"//div[textarea[@id='description']]//iframe")
    tinymce_description_field = (By.ID, "tinymce")
    issue_assign_to_me_link = (By.ID, 'assign-to-me-trigger')
    issue_resolution_field = (By.ID, 'resolution')
    issue_type_field = (By.ID, 'issuetype-field')
    issue_type_dropdown_elements = (By.CLASS_NAME, "aui-list-item")
    issue_ready_to_save_spinner = (By.CSS_SELECTOR, ".buttons>.throbber")
    issue_submit_button = (By.ID, "create-issue-submit")

    # Edit Issue page
    edit_issue_page = (By.ID, "issue-edit")
    edit_issue_description = (By.ID, 'description')
    edit_issue_submit = (By.ID, 'issue-edit-submit')

class ProjectLocators:

    project_summary_property_column = (By.CLASS_NAME, 'project-meta-column')


class SearchLocators:

    search_issue_table = (By.ID, "issuetable")
    search_issue_content = (By.ID, "issue-content")
    search_no_issue_found = (By.ID, "issue-content")
