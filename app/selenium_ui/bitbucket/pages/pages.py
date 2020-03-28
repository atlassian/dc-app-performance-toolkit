from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.bitbucket.pages.selectors import BaseLocator, LoginPageLocators, GetStartedLocators, \
    DashboardLocators, ProjectsLocators, ProjectLocators, RepoLocators, RepoNavigationPanelLocators, PopupLocators, \
    PullRequestLocator, BranchesLocator, RepositorySettingsLocator, UserSettingsLocator, RepoCommitsLocator, \
    LogoutPageLocators, UrlManager


class LoginPage(BasePage):
    page_url = UrlManager()

    def at(self):
        return self.verify_url(LoginPageLocators.login_params)

    def fill_username(self, username):
        self.get_element(LoginPageLocators.username_textfield).send_keys(username)

    def fill_password(self, password):
        self.get_element(LoginPageLocators.password_textfield).send_keys(password)

    def submit_login(self, interaction=None):
        self.wait_until_visible(LoginPageLocators.submit_button, interaction).click()

    def set_credentials(self, username, password):
        self.fill_username(username)
        self.fill_password(password)

    def get_app_version(self):
        el = self.get_element(LoginPageLocators.application_version)
        return ''.join([i for i in el.text.split('.')[0] if i.isdigit()])


class LogoutPage(BasePage):

    page_url = LogoutPageLocators.logout_url


class GetStarted(BasePage):
    page_url = GetStartedLocators.get_started_url

    def at(self):
        return self.verify_url(GetStartedLocators.get_started_params)

    def get_started_widget_visible(self, interaction=None):
        return self.wait_until_present(GetStartedLocators.bitbucket_is_ready_widget, interaction)


class Dashboard(BasePage):
    page_url = DashboardLocators.dashboard_url

    def at(self):
        return self.verify_url(DashboardLocators.dashboard_params)

    def dashboard_presented(self, interaction):
        return self.wait_until_present(DashboardLocators.dashboard_presence, interaction)


class Projects(BasePage):
    page_url = ProjectsLocators.project_url

    def at(self):
        return self.verify_url(ProjectsLocators.projects_params)

    def projects_list_presented(self, interaction):
        return self.wait_until_present(ProjectsLocators.projects_list, interaction)


class Project(BasePage):

    def __init__(self, driver, project_key):
        BasePage.__init__(self, driver)
        self.project_key = project_key
        url_manager = UrlManager(host=BaseLocator.host, project_key=project_key)
        self.page_url = url_manager.project_url()
        self.params_to_verify = url_manager.project_params

    def at(self):
        return self.verify_url(self.params_to_verify)

    def repositories_visible(self, interaction):
        return self.wait_until_visible(ProjectLocators.repositories_container, interaction) \
               and self.wait_until_visible(ProjectLocators.repository_name, interaction)


class RepoNavigationPanel(BasePage):

    def __clone_repo_button(self):
        return self.get_element(RepoNavigationPanelLocators.clone_repo_button)

    def wait_navigation_panel_presented(self, interaction):
        return self.wait_until_present(RepoNavigationPanelLocators.navigation_panel, interaction)

    def clone_repo_click(self):
        self.__clone_repo_button().click()

    def fork_repo(self, interaction):
        return self.wait_until_visible(RepoNavigationPanelLocators.fork_repo_button, interaction)

    def create_pull_request(self, interaction):
        self.wait_until_visible(RepoNavigationPanelLocators.create_pull_request_button, interaction).click()
        self.wait_until_visible(RepoLocators.pull_requests_list, interaction)


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.default_popup, PopupLocators.popup_1, PopupLocators.popup_2)


class Repository(BasePage):

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(host=BaseLocator.host, project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.repo_url()
        self.params_to_verify = url_manager.repo_params_browse
        self.repo_slug = repo_slug
        self.project_key = project_key

    def at(self):
        return self.verify_url(self.params_to_verify)

    def set_enable_fork_sync(self, interaction, value):
        checkbox = self.wait_until_visible(RepoLocators.repo_fork_sync, interaction)
        current_state = checkbox.is_selected()
        if (value and not current_state) or (not value and current_state):
            checkbox.click()

    def submit_fork_repo(self):
        self.wait_until_visible(RepoLocators.fork_repo_submit_button).click()

    def set_fork_repo_name(self):
        fork_name_field = self.get_element(RepoLocators.fork_name_field)
        fork_name_field.clear()
        fork_name = f"{self.repo_slug}-{self.generate_random_string(5)}"
        fork_name_field.send_keys(fork_name)
        return fork_name


class RepoPullRequests(BasePage):

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(host=BaseLocator.host, project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.repo_pull_requests()
        self.params_to_verify = url_manager.repo_pull_requests_params

    def at(self):
        return self.verify_url(self.params_to_verify)

    def pull_requests_list_visible(self, interaction):
        return self.wait_until_visible(RepoLocators.pull_requests_list, interaction)

    def create_new_pull_request(self, interaction):
        self.wait_until_visible(RepoLocators.create_pull_request_button, interaction).click()
        self.wait_until_visible(RepoLocators.new_pull_request_branch_compare_window, interaction)

    def set_pull_request_source_branch(self, interaction, source_branch):
        self.wait_until_visible(RepoLocators.pr_source_branch_field, interaction).click()
        self.wait_until_visible(RepoLocators.pr_branches_dropdown, interaction)
        source_branch_name_field = self.get_element(RepoLocators.pr_source_branch_name)
        source_branch_name_field.send_keys(source_branch)
        self.wait_until_invisible(RepoLocators.pr_source_branch_spinner, interaction)
        source_branch_name_field.send_keys(Keys.ENTER)
        self.wait_until_invisible(RepoLocators.pr_branches_dropdown, interaction)

    def set_pull_request_destination_repo(self, interaction):
        self.wait_until_visible(RepoLocators.pr_destination_repo_field, interaction).click()
        self.wait_until_visible(RepoLocators.pr_destination_first_repo_dropdown, interaction).click()

    def set_pull_request_destination_branch(self, interaction, destination_branch):
        self.wait_until_visible(RepoLocators.pr_destination_branch_field, interaction)
        self.execute_js("document.querySelector('#targetBranch').click()")
        self.wait_until_visible(RepoLocators.pr_destination_branch_dropdown, interaction)
        destination_branch_name_field = self.get_element(RepoLocators.pr_destination_branch_name)
        destination_branch_name_field.send_keys(destination_branch)
        self.wait_until_invisible(RepoLocators.pr_destination_branch_spinner, interaction)
        destination_branch_name_field.send_keys(Keys.ENTER)
        self.wait_until_invisible(RepoLocators.pr_branches_dropdown, interaction)
        self.wait_until_clickable(RepoLocators.pr_continue_button, interaction)
        self.wait_until_visible(RepoLocators.pr_continue_button, interaction).click()

    def submit_pull_request(self, interaction):
        self.wait_until_visible(RepoLocators.pr_description_field, interaction)
        title = self.get_element(RepoLocators.pr_title_field)
        title.clear()
        title.send_keys('Selenium test pull request')
        self.wait_until_visible(RepoLocators.pr_submit_button, interaction).click()
        self.wait_until_visible(PullRequestLocator.pull_request_activity_content, interaction)
        self.wait_until_clickable(PullRequestLocator.pull_request_page_merge_button, interaction)


class PullRequest(BasePage):

    def __init__(self, driver, project_key=None, repo_slug=None, pull_request_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(host=BaseLocator.host, project_key=project_key, repo_slug=repo_slug,
                                 pull_request_key=pull_request_key)
        self.page_url = url_manager.pull_request_overview()
        self.params_to_verify_overview = url_manager.pull_request_params_overview
        self.diff_url = url_manager.pull_request_diff()
        self.commits_url = url_manager.pull_request_commits()

    def at(self):
        return self.verify_url(self.params_to_verify_overview)

    def pull_request_tab_presented(self, interaction):
        return self.wait_until_visible(PullRequestLocator.tab_panel, interaction)

    def go_to_overview(self):
        return self.go_to()

    def go_to_diff(self):
        self.go_to_url(url=self.diff_url)

    def go_to_commits(self):
        self.go_to_url(self.commits_url)

    def wait_diff_tab_presented(self, interaction):
        return self.wait_until_any_element_visible(PullRequestLocator.commit_files, interaction)

    def wait_code_diff_to_be_visible(self, interaction):
        return self.wait_until_visible(PullRequestLocator.diff_code_lines, interaction)

    def wait_commit_msg_label(self, interaction):
        self.wait_until_any_element_visible(PullRequestLocator.commit_message_label, interaction)

    def click_inline_comment_button_js(self):
        selector = self.get_selector(PullRequestLocator.inline_comment_button)
        self.execute_js(f"elems=document.querySelectorAll('{selector[1]}'); "
                        "item=elems[Math.floor(Math.random() * elems.length)];"
                        "item.scrollIntoView();"
                        "item.click();")

    def wait_comment_text_area_visible(self, interaction):
        return self.wait_until_visible(PullRequestLocator.comment_text_area, interaction)

    def add_code_comment_v6(self, interaction):
        self.wait_comment_text_area_visible(interaction)
        selector = self.get_selector(PullRequestLocator.comment_text_area)
        self.execute_js(f"document.querySelector('{selector[1]}').value = 'Comment from Selenium script';")
        self.click_save_comment_button(interaction)

    def add_code_comment_v7(self, interaction):
        self.wait_until_visible(PullRequestLocator.text_area, interaction).send_keys('Comment from Selenium script')
        self.click_save_comment_button(interaction)

    def click_save_comment_button(self, interaction):
        return self.wait_until_visible(PullRequestLocator.comment_button, interaction).click()

    def wait_pull_request_activity_visible(self, interaction):
        return self.wait_until_visible(PullRequestLocator.pull_request_activity_content, interaction)

    def add_overview_comment(self, interaction):
        self.wait_until_clickable(PullRequestLocator.text_area, interaction).send_keys(self.generate_random_string(50))

    def wait_merge_button_clickable(self, interaction):
        self.wait_until_clickable(PullRequestLocator.pull_request_page_merge_button, interaction)

    def merge_pull_request(self, interaction):
        if self.driver.app_version == '6':
            self.wait_until_present(PullRequestLocator.merge_spinner, interaction, time_out=1)
            self.wait_until_invisible(PullRequestLocator.merge_spinner, interaction)
        self.wait_until_present(PullRequestLocator.pull_request_page_merge_button).click()
        PopupManager(self.driver).dismiss_default_popup()
        self.wait_until_visible(PullRequestLocator.diagram_selector)
        self.wait_until_clickable(PullRequestLocator.pull_request_modal_merge_button, interaction).click()
        self.wait_until_invisible(PullRequestLocator.del_branch_checkbox_selector, interaction)


class RepositoryBranches(BasePage):

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(host=BaseLocator.host, project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.repo_branches()
        self.params_to_verify = url_manager.branches_params

    def at(self):
        self.verify_url(self.params_to_verify)

    def wait_branch_name_visible(self, interaction):
        self.wait_until_any_element_visible(BranchesLocator.branches_name, interaction)


class RepositorySettings(BasePage):

    def wait_repository_settings(self, interaction):
        self.wait_until_visible(RepositorySettingsLocator.repository_settings_menu, interaction)

    def delete_repository(self, interaction, repo_slug):
        self.wait_repository_settings(interaction)
        self.wait_until_visible(RepositorySettingsLocator.delete_repository_button, interaction).click()
        self.wait_until_visible(RepositorySettingsLocator.delete_repository_modal_text_field,
                                interaction).send_keys(repo_slug)
        self.wait_until_clickable(RepositorySettingsLocator.delete_repository_modal_submit_button, interaction)
        self.wait_until_visible(RepositorySettingsLocator.delete_repository_modal_submit_button, interaction).click()


class ForkRepositorySettings(RepositorySettings):
    def __init__(self, driver, user, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(host=BaseLocator.host, user=user, repo_slug=repo_slug)
        self.page_url = url_manager.fork_repo_url()
        self.params_to_verify = url_manager.fork_repo_params

    def at(self):
        self.verify_url(self.params_to_verify)


class UserSettings(BasePage):

    def __init__(self, driver, user):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(host=BaseLocator.host, user=user)
        self.page_url = url_manager.user_settings_url()
        self.params_to_verify = url_manager.user_settings_params

    def at(self):
        self.verify_url(self.params_to_verify)

    def user_role_visible(self, interaction):
        return self.wait_until_visible(UserSettingsLocator.user_role_label, interaction)


class RepositoryCommits(BasePage):
    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(host=BaseLocator.host, project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.commits_url()
        self.params_to_verify = url_manager.repo_commits_params

    def at(self):
        self.verify_url(self.params_to_verify)

    def commit_graph_is_visible(self, interaction):
        self.wait_until_any_element_visible(RepoCommitsLocator.repo_commits_graph, interaction)
