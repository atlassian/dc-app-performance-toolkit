from selenium.webdriver.common.by import By
from util.conf import BITBUCKET_SETTINGS


class UrlManager:

    def __init__(self, user=None, project_key=None, repo_slug=None, pull_request_key=None):
        self.host = BITBUCKET_SETTINGS.server_url
        self.user = user
        self.project_key = project_key
        self.repo_slug = repo_slug
        self.project_params = f'/projects/{self.project_key}'
        self.repo_params_browse = f'/projects/{self.project_key}/repos/{self.repo_slug}/browse'
        self.repo_params = f'/projects/{self.project_key}/repos/{self.repo_slug}'
        self.repo_pull_requests_params = f'{self.repo_params}/pull-requests'
        self.pull_request_params_overview = f'{self.repo_params}/pull-requests/{pull_request_key}/overview'
        self.pull_request_params_diff = f'{self.repo_params}/pull-requests/{pull_request_key}/diff'
        self.pull_request_params_commits = f'{self.repo_params}/pull-requests/{pull_request_key}/commits'
        self.branches_params = f'{self.repo_params}/branches'
        self.fork_repo_params = f'/users/{self.user}/repos/{self.repo_slug}/settings'
        self.user_settings_params = f'/users/{self.user}'
        self.repo_commits_params = f'{self.repo_params}/commits'
        self.login_params = '/login?next=/getting-started'
        self.logout_params = '/j_atl_security_logout'
        self.get_started_params = '/getting-started'
        self.dashboard_params = '/dashboard'
        self.projects_params = '/projects'
        self.branches_base_branch = f'/projects/{self.project_key}/repos/{self.repo_slug}/branches?base='

    def create_pull_request_url(self, from_branch, to_branch):
        return f"{self.host}/projects/{self.project_key}/repos/{self.repo_slug}/pull-requests?create&targetBranch=" \
               f"refs%2Fheads%2F{to_branch}&sourceBranch=refs%2Fheads%2F{from_branch}"

    def base_branch_url(self):
        return f"{self.host}{self.branches_base_branch}"

    def project_url(self):
        return f"{self.host}{self.project_params}"

    def repo_url(self):
        return f"{self.host}{self.repo_params_browse}"

    def repo_pull_requests(self):
        return f"{self.host}{self.repo_pull_requests_params}"

    def repo_branches(self):
        return f"{self.host}{self.branches_params}"

    def pull_request_overview(self):
        return f"{self.host}{self.pull_request_params_overview}"

    def pull_request_diff(self):
        return f"{self.host}{self.pull_request_params_diff}"

    def pull_request_commits(self):
        return f"{self.host}{self.pull_request_params_commits}"

    def fork_repo_url(self):
        return f"{self.host}{self.fork_repo_params}"

    def user_settings_url(self):
        return f"{self.host}{self.user_settings_params}"

    def commits_url(self):
        return f"{self.host}{self.repo_commits_params}"

    def login_url(self):
        return f"{self.host}{self.login_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"

    def get_started_url(self):
        return f"{self.host}{self.get_started_params}"

    def dashboard_url(self):
        return f"{self.host}{self.dashboard_params}"

    def projects_url(self):
        return f"{self.host}{self.projects_params}"


class PopupLocators:
    default_popup = '.feature-discovery-close'
    popup_1 = '.css-1it7f5o'
    popup_2 = 'button.aui-button-link.feature-discovery-close'
    popup_3 = '.css-15p34h1'
    popup_4 = '.css-1dqf51u'


class LoginPageLocators:
    login_params = UrlManager().login_params
    login_url = UrlManager().login_url()

    submit_button = (By.ID, "submit")
    username_textfield = (By.ID, "j_username")
    password_textfield = (By.ID, "j_password")
    application_version = (By.ID, 'product-version')
    node_id = (By.CLASS_NAME, 'footer-body')


class LogoutPageLocators:
    logout_params = UrlManager().logout_params
    logout_url = UrlManager().logout_url()


class GetStartedLocators:
    get_started_params = UrlManager().get_started_params
    get_started_url = UrlManager().get_started_url()
    user_profile_icon = (By.ID, 'current-user')


class DashboardLocators:
    dashboard_params = UrlManager().dashboard_params
    dashboard_url = UrlManager().dashboard_url()

    dashboard_presence = (By.TAG_NAME, 'h2')


class ProjectsLocators:
    projects_params = UrlManager().projects_params
    project_url = UrlManager().projects_url()

    projects_list = (By.ID, "projects-container")


class ProjectLocators:

    repositories_container = (By.ID, "repositories-container")
    repository_name = (By.CSS_SELECTOR, "span.repository-name")


class RepoNavigationPanelLocators:

    navigation_panel = (By.CSS_SELECTOR, '.aui-navgroup-vertical>.aui-navgroup-inner')
    clone_repo_button = (By.CSS_SELECTOR, '.clone-repo>#clone-repo-button')

    fork_repo_button = (By.CSS_SELECTOR, 'span.icon-fork')

    create_pull_request_button = (By.CSS_SELECTOR, '.aui-sidebar-group.sidebar-navigation>ul>li:nth-child(4)')


class RepoLocators:

    pull_requests_list = (By.ID, 'pull-requests-content')
    repo_fork_sync = (By.ID, "enable-ref-syncing")
    fork_name_field = (By.ID, 'name')
    fork_repo_submit_button = (By.ID, "fork-repo-submit")
    create_pull_request_button = (By.ID, 'empty-list-create-pr-button')
    new_pull_request_branch_compare_window = (By.ID, 'branch-compare')

    pr_source_branch_field = (By.ID, 'sourceBranch')
    pr_branches_dropdown = (By.CSS_SELECTOR, 'ul.results-list')
    pr_source_branch_name = (By.ID, 'sourceBranchDialog-search-input')
    pr_source_branch_spinner = (By.CSS_SELECTOR, '#sourceBranchDialog>div.results>div.spinner-wrapper')

    pr_destination_repo_field = (By.ID, 'targetRepo')
    pr_destination_first_repo_dropdown = (By.CSS_SELECTOR, 'div#targetRepoDialog>div>ul.results-list>li:nth-child(1)')

    pr_destination_branch_field = (By.ID, 'targetBranch')
    pr_destination_branch_dropdown = (By.ID, 'targetBranchDialog')
    pr_destination_branch_name = (By.ID, 'targetBranchDialog-search-input')
    pr_destination_branch_spinner = (By.CSS_SELECTOR, '#targetBranchDialog>div.results>div.spinner-wrapper')

    pr_continue_button = (By.ID, 'show-create-pr-button')
    pr_description_field = (By.CSS_SELECTOR, 'textarea#pull-request-description')
    pr_title_field = (By.ID, 'title')
    pr_submit_button = (By.ID, 'submit-form')


class PullRequestLocator:

    tab_panel = (By.CSS_SELECTOR, 'ul.tabs-menu')

    commit_files = (By.CSS_SELECTOR, '.changes-sidebar>.changes-scope-content')
    diff_code_lines = (By.CLASS_NAME, "diff-segment")

    commit_message_label = (By.CSS_SELECTOR, 'tr>th.message')
    inline_comment_button = (By.CSS_SELECTOR, ".diff-line-comment-trigger")
    comment_text_area = (By.CLASS_NAME, "comment-editor-wrapper")
    text_area = (By.CLASS_NAME, 'CodeMirror-code')
    comment_button = (By.CSS_SELECTOR, "div.editor-controls>button:nth-child(1)")
    pull_request_activity_content = (By.CSS_SELECTOR, ".pull-request-activities")

    pull_request_page_merge_button = (By.CLASS_NAME, 'merge-button')

    merge_spinner = (By.CSS_SELECTOR, "aui-spinner[size='small']")
    diagram_selector = (By.CLASS_NAME, 'branches-diagram')
    merge_diagram_selector = (By.CLASS_NAME, "merge-diagram")
    pull_request_modal_merge_button = (By.CSS_SELECTOR, ".merge-dialog button[type='submit']")
    del_branch_checkbox_selector = (By.NAME, 'deleteSourceRef')
    delete_branch_per_merge_checkbox = (By.CSS_SELECTOR, "input[type='checkbox']")


class BranchesLocator:

    branches_name = (By.ID, "branch-name-column")
    branches_action = (By.ID, "branch-actions")
    branches_action_create_branch = (By.CSS_SELECTOR, "a.create-branch")
    new_branch_name_textfield = (By.CSS_SELECTOR, "input.text.branch-name")
    new_branch_submit_button = (By.ID, "create-branch-submit")
    search_branch_textfield = (By.ID, 'paged-table-input-for-branch-list')
    search_branch_action = (By.CSS_SELECTOR, '.branch-actions-column>button')
    search_action_delete_branch = (By.CSS_SELECTOR, 'li>a.delete-branch')
    delete_branch_dialog_submit = (By.ID, 'delete-branch-dialog-submit')


class RepositorySettingsLocator:
    repository_settings_menu = (By.CSS_SELECTOR, 'div.aui-page-panel-nav')
    delete_repository_button = (By.ID, 'repository-settings-delete-button')
    delete_repository_modal_text_field = (By.ID, 'confirmRepoName')
    delete_repository_modal_submit_button = (By.ID, 'delete-repository-dialog-submit')


class UserSettingsLocator:
    user_role_label = (By.CSS_SELECTOR, 'div.user-detail.username')


class RepoCommitsLocator:
    repo_commits_graph = (By.ID, 'commits-table')
