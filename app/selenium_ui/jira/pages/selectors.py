from selenium.webdriver.common.by import By
from util.conf import JIRA_SETTINGS


class PopupLocators:
    default_popup = '.aui-message .icon-close'
    popup_1 = 'form.tip-footer>.helptip-close'
    popup_2 = '.aui-inline-dialog-contents .cancel'


class UrlManager:

    def __init__(self, issue_key=None, issue_id=None, project_key=None, jql=None, projects_list_page=None,
                 board_id=None, page_key=None):
        self.host = JIRA_SETTINGS.server_url
        self.login_params = '/login.jsp'
        self.logout_params = '/logoutconfirm.jsp'
        self.dashboard_params = '/secure/Dashboard.jspa'
        self.issue_params = f"/browse/{issue_key}"
        self.project_summary_params = f"/projects/{project_key}/summary"
        self.jql_params = f"/issues/?jql={jql}"
        self.edit_issue_params = f"/secure/EditIssue!default.jspa?id={issue_id}"
        self.edit_comments_params = f"/secure/AddComment!default.jspa?id={issue_id}"
        self.projects_list_params = f'/secure/BrowseProjects.jspa?selectedCategory=all&selectedProjectType=all&page=' \
                                    f'{projects_list_page}'
        self.boards_list_params = '/secure/ManageRapidViews.jspa'
        self.scrum_board_backlog_params = f"/secure/RapidBoard.jspa?rapidView={board_id}&view=planning"
        self.scrum_board_params = f"/secure/RapidBoard.jspa?rapidView={board_id}"
        self.page_url = f"/wiki/p/{project_key}/view/{page_key}"
        self.page_edit_url = f"/wiki/p/{project_key}/view/{page_key}/edit"
        self.pages_list = f"/wiki/p/{project_key}/view"

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

    def edit_comments_url(self):
        return f"{self.host}{self.edit_comments_params}"

    def projects_list_page_url(self):
        return f"{self.host}{self.projects_list_params}"

    def boards_list_page_url(self):
        return f"{self.host}{self.boards_list_params}"

    def scrum_board_backlog_url(self):
        return f"{self.host}{self.scrum_board_backlog_params}"

    def scrum_board_url(self):
        return f"{self.host}{self.scrum_board_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"

    def create_sw_page_url(self):
        return f"{self.host}{self.page_url}"

    def create_sw_editor_page(self):
        return f"{self.host}{self.page_edit_url}"

    def create_sw_pages_list(self):
        return f"{self.host}{self.pages_list}"


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
    system_dashboard = (By.ID, "dashboard")


class LogoutLocators:
    logout_url = UrlManager().logout_url()
    logout_submit_button = (By.ID, "confirm-logout-submit")
    login_button_link = (By.CLASS_NAME, "login-link")


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
    issue_description_field_RTE = (By.XPATH, "//div[textarea[@id='description']]//iframe")
    issue_description_field = (By.XPATH, "//textarea[@id='description']")
    tinymce_description_field = (By.ID, "tinymce")
    issue_assign_to_me_link = (By.ID, 'assign-to-me-trigger')
    issue_resolution_field = (By.ID, 'resolution')
    issue_type_field = (By.ID, 'issuetype-field')
    issue_types_options = (By.ID, "issuetype-options")
    issue_type_dropdown_elements = (By.CLASS_NAME, "aui-list-item")
    issue_ready_to_save_spinner = (By.CSS_SELECTOR, ".buttons>.throbber")
    issue_submit_button = (By.ID, "create-issue-submit")

    # Edit Issue page
    edit_issue_page = (By.ID, "issue-edit")
    edit_issue_description = (By.ID, 'description')
    edit_issue_submit = (By.ID, 'issue-edit-submit')

    # Edit Comments page
    edit_comment_add_comment_button = (By.ID, "comment-add-submit")
    edit_comment_text_field_RTE = (By.XPATH, "//div[textarea[@id='comment']]//iframe")
    edit_comment_text_field = (By.XPATH, "//textarea[@id='comment']")


class ProjectLocators:
    project_summary_property_column = (By.CLASS_NAME, 'project-meta-column')

    # projects list locators
    projects_list = (By.CSS_SELECTOR, "tbody.projects-list")
    projects_not_found = (By.CLASS_NAME, "none-panel")


class SearchLocators:
    search_issue_table = (By.ID, "issuetable")
    search_issue_content = (By.ID, "issue-content")
    search_no_issue_found = (By.CLASS_NAME, "no-results-message")


class BoardsListLocators:
    boards_list_url = UrlManager().boards_list_page_url()
    boards_list_params = UrlManager().boards_list_params

    boards_list = (By.CSS_SELECTOR, "#ghx-content-main table.aui")


class BoardLocators:
    # Scrum boards
    scrum_board_backlog_content = (By.CSS_SELECTOR, "#ghx-backlog[data-rendered]:not(.browser-metrics-stale)")
    board_columns = (By.CSS_SELECTOR, ".ghx-column")


class SimpleWikiPageLocator:
    sw_page = (By.XPATH, '//*[@id="content"]/div[1]/div/div[2]/div/div[1]')
    sw_page_comment = (By.XPATH, '//input[@placeholder="What do you want to say?"]')
    sw_page_comment_textfield = (By.CLASS_NAME, 'ProseMirror')
    sw_comment_block = (By.XPATH, '//*[@data-test-id="page-comments"]')
    sw_comment_save = (
        By.XPATH, '//*[@data-test-id="page-comments"]/div[last()]/div[2]/div/div[2]/div[2]/div/div[1]/button')


class SimpleWikiPageEditorLocator:
    sw_page_editor = (By.XPATH, '//*[@id="content"]/div[1]/div/div[2]/div/div/form/div/div[2]')
    sw_page_editor_textfield_location = (By.CLASS_NAME, "ProseMirror")
    sw_page_editor_title_location = (By.NAME, "title")
    sw_page_editor_save_button = (
        By.XPATH, '//form/div/div[2]/div/div[2]/div/div[1]/button')


class SimpleWikiPagesListLocator:
    sw_add_page_dialog = (By.XPATH, '//*[@data-test-id="dialog-page-add"]')
    sw_add_page = (By.XPATH, '//*[@data-test-id="page-header"]/div/div/div[2]/button')
    sw_pages_table = (By.XPATH, '//*[@data-test-id="container-page-list"]/div[3]/div/table')
    sw_add_page_title = (By.XPATH, '//input[@name="title"]')
    sw_create_page = (By.XPATH, '//div[@data-test-id="dialog-page-add"]/footer/div/div[1]/button')
