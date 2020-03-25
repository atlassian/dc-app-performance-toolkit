from selenium.webdriver.common.by import By
from util.conf import BITBUCKET_SETTINGS


class BaseLocator:
    host = f"{BITBUCKET_SETTINGS.server_url}"


class PopupLocators:
    default_popup = '.feature-discovery-close'
    popup_1 = '.css-1it7f5o'
    popup_2 = 'button.aui-button-link.feature-discovery-close'


class LoginPageLocators:
    login_params = '/login?next=/getting-started'
    login_url = f"{BaseLocator.host}{login_params}"

    submin_button = {'6': (By.ID, "submit"), '7': (By.ID, "submit")}
    username_textfield = {'6': (By.ID, "j_username"), '7': (By.ID, "j_username")}
    password_textfield = {'6': (By.ID, "j_password"), '7': (By.ID, "j_password")}
    application_version = (By.ID, 'product-version')


class LogoutPageLocators:
    logout_params = '/j_atl_security_logout'
    logout_url = f"{BaseLocator.host}{logout_params}"


class GetStartedLocators:
    get_started_params = '/getting-started'
    get_started_url = f"{BaseLocator.host}{get_started_params}"

    bitbucket_is_ready_widget = {'6': (By.CLASS_NAME, "marketing-page-footer"),
                                 '7': (By.CLASS_NAME, "marketing-page-footer")}


class DashboardLocators:
    dashboard_params = '/dashboard'
    dashboard_url = f'{BaseLocator.host}{dashboard_params}'

    dashboard_presens = {'6': (By.CLASS_NAME, 'dashboard-your-work'), '7': (By.CLASS_NAME, 'dashboard-your-work')}


class ProjectsLocators:
    projects_params = '/projects'
    project_url = f"{BaseLocator.host}{projects_params}"

    projects_list = {'6': (By.ID, "projects-container"), '7': (By.ID, "projects-container")}


class ProjectLocators:

    repositories_container = {'6': (By.ID, "repositories-container"), '7': (By.ID, "repositories-container")}
    repository_name = {'6': (By.CSS_SELECTOR, "span.repository-name"), '7': (By.CSS_SELECTOR, "span.repository-name")}


class RepoNavigationPanelLocators:

    navigation_panel = {'6': (By.CSS_SELECTOR, '.aui-navgroup-vertical>.aui-navgroup-inner'),
                        '7': (By.CSS_SELECTOR, '.aui-navgroup-vertical>.aui-navgroup-inner')}
    clone_repo_button = {'6': (By.CSS_SELECTOR, '.clone-repo>#clone-repo-button'),
                         '7': (By.CSS_SELECTOR, '.clone-repo>#clone-repo-button')}

    fork_repo_button = (By.CSS_SELECTOR, 'span.icon-fork')

    create_pull_request_button = (By.CSS_SELECTOR, '.aui-sidebar-group.sidebar-navigation>ul>li:nth-child(4)')


class RepoLocators:

    pull_requests_list = {'6': (By.ID, 'pull-requests-content'), '7': (By.ID, 'pull-requests-content')}
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

    tab_panel = {'6': (By.CSS_SELECTOR, 'ul.tabs-menu'), '7': (By.CSS_SELECTOR, 'ul.tabs-menu')}
    commit_files = {'6':(By.CSS_SELECTOR, '.commit-files>.file-tree-container'),
                    '7': (By.CSS_SELECTOR, '.changes-sidebar>.changes-scope-content')}
    diff_code_lines = {'6': (By.CLASS_NAME, 'CodeMirror-code'),
                       '7': (By.CLASS_NAME, "diff-segment")}

    commit_message_label = (By.CSS_SELECTOR, 'tr>th.message')
    inline_comment_button = {'6': (By.CSS_SELECTOR, "button.add-comment-trigger>span.aui-iconfont-add-comment"),
                             '7': (By.CSS_SELECTOR, ".diff-line-comment-trigger")}
    comment_text_area = {'6': (By.CSS_SELECTOR, "textarea.text"), '7': (By.CLASS_NAME, "comment-editor-wrapper")}
    text_area = {'6': (By.CSS_SELECTOR, 'textarea.text'), '7': (By.CLASS_NAME, 'CodeMirror-code')}
    comment_button = {'6': (By.CSS_SELECTOR, "div.buttons>button:nth-child(1)"),
                      '7': (By.CSS_SELECTOR, "div.editor-controls>button:nth-child(1)")}
    pull_request_activity_content = {'6': (By.CSS_SELECTOR, ".pull-request-activity-content"),
                                     '7': (By.CSS_SELECTOR, ".pull-request-activities")}

    pull_request_page_merge_button = (By.CLASS_NAME, 'merge-button')

    merge_spinner = (By.CSS_SELECTOR, "aui-spinner[size='small']")
    diagram_selector = {'6': (By.CSS_SELECTOR, 'div.diagram-image'), '7': (By.CLASS_NAME, 'branches-diagram')}
    pull_request_modal_merge_button = {'6': (By.CSS_SELECTOR, 'button.confirm-button'),
                                       '7': (By.CSS_SELECTOR, "button[type='submit']")}
    del_branch_checkbox_selector = {'6': (By.CSS_SELECTOR, 'span.pull-request-cleanup-checkbox-wrapper'),
                                    '7': (By.NAME, 'deleteSourceRef')}


class BranchesLocator:

    branches_name = (By.ID, "branch-name-column")


class RepositorySettingsLocator:
    repository_settings_menu = (By.CSS_SELECTOR, 'div.aui-page-panel-nav')
    delete_repository_button = (By.ID, 'repository-settings-delete-button')
    delete_repository_modal_text_field = (By.ID, 'confirmRepoName')
    delete_repository_modal_submit_button = (By.ID, 'delete-repository-dialog-submit')


class UserSettingsLocator:
    user_role_label = (By.CSS_SELECTOR, 'div.user-detail.username')

class RepoCommitsLocator:
    repo_commits_graph = (By.CSS_SELECTOR, 'svg.commit-graph')