from selenium.webdriver.common.keys import Keys

from selenium_ui.base_page import BasePage
from selenium_ui.bitbucket.pages.selectors import LoginPageLocators, GetStartedLocators, \
    DashboardLocators, ProjectsLocators, ProjectLocators, RepoLocators, RepoNavigationPanelLocators, PopupLocators, \
    PullRequestLocator, BranchesLocator, RepositorySettingsLocator, UserSettingsLocator, RepoCommitsLocator, \
    LogoutPageLocators, UrlManager


class LoginPage(BasePage):
    page_url = UrlManager().login_url()

    def fill_username(self, username):
        self.get_element(LoginPageLocators.username_textfield).send_keys(username)

    def fill_password(self, password):
        self.get_element(LoginPageLocators.password_textfield).send_keys(password)

    def submit_login(self):
        self.wait_until_visible(LoginPageLocators.submit_button).click()

    def set_credentials(self, username, password):
        self.fill_username(username)
        self.fill_password(password)

    def get_app_version(self):
        text = self.get_element(LoginPageLocators.application_version).text
        return text.replace('v', '')

    def get_app_major_version(self):
        return self.get_app_version().split('.')[0]

    def get_node_id(self):
        text = self.get_element(LoginPageLocators.node_id).text
        return text.split('\n')[2]

    def is_logged_in(self):
        elements = self.get_elements(GetStartedLocators.user_profile_icon)
        return True if elements else False


class LogoutPage(BasePage):

    page_url = LogoutPageLocators.logout_url


class GetStarted(BasePage):
    page_url = GetStartedLocators.get_started_url
    page_loaded_selector = GetStartedLocators.user_profile_icon


class Dashboard(BasePage):
    page_url = DashboardLocators.dashboard_url
    page_loaded_selector = DashboardLocators.dashboard_presence


class Projects(BasePage):
    page_url = ProjectsLocators.project_url
    page_loaded_selector = ProjectsLocators.projects_list


class Project(BasePage):
    page_loaded_selector = [ProjectLocators.repositories_container, ProjectLocators.repository_name]

    def __init__(self, driver, project_key):
        BasePage.__init__(self, driver)
        self.project_key = project_key
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.project_url()


class RepoNavigationPanel(BasePage):
    page_loaded_selector = RepoNavigationPanelLocators.navigation_panel

    def __clone_repo_button(self):
        return self.get_element(RepoNavigationPanelLocators.clone_repo_button)

    def wait_for_navigation_panel(self):
        return self.wait_until_present(RepoNavigationPanelLocators.navigation_panel)

    def clone_repo_click(self):
        self.__clone_repo_button().click()

    def fork_repo(self):
        return self.wait_until_visible(RepoNavigationPanelLocators.fork_repo_button)

    def create_pull_request(self):
        self.wait_until_visible(RepoNavigationPanelLocators.create_pull_request_button).click()
        self.wait_until_visible(RepoLocators.pull_requests_list)


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.default_popup, PopupLocators.popup_1, PopupLocators.popup_2,
                                  PopupLocators.popup_3, PopupLocators.popup_4)


class Repository(BasePage):

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.repo_url()
        self.repo_slug = repo_slug
        self.project_key = project_key

    def set_enable_fork_sync(self, value):
        checkbox = self.wait_until_visible(RepoLocators.repo_fork_sync)
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
    page_loaded_selector = RepoLocators.pull_requests_list

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        self.url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug)
        self.page_url = self.url_manager.repo_pull_requests()

    def create_new_pull_request(self, from_branch, to_branch):
        self.go_to_url(url=self.url_manager.create_pull_request_url(from_branch=from_branch,
                                                                    to_branch=to_branch))
        self.submit_pull_request()

    def set_pull_request_source_branch(self, source_branch):
        self.wait_until_visible(RepoLocators.pr_source_branch_field).click()
        self.wait_until_visible(RepoLocators.pr_branches_dropdown)
        source_branch_name_field = self.get_element(RepoLocators.pr_source_branch_name)
        source_branch_name_field.send_keys(source_branch)
        self.wait_until_invisible(RepoLocators.pr_source_branch_spinner)
        source_branch_name_field.send_keys(Keys.ENTER)
        self.wait_until_invisible(RepoLocators.pr_branches_dropdown)

    def set_pull_request_destination_repo(self):
        self.wait_until_visible(RepoLocators.pr_destination_repo_field).click()
        self.wait_until_visible(RepoLocators.pr_destination_first_repo_dropdown).click()

    def set_pull_request_destination_branch(self, destination_branch):
        self.wait_until_visible(RepoLocators.pr_destination_branch_field)
        self.execute_js("document.querySelector('#targetBranch').click()")
        self.wait_until_visible(RepoLocators.pr_destination_branch_dropdown)
        destination_branch_name_field = self.get_element(RepoLocators.pr_destination_branch_name)
        destination_branch_name_field.send_keys(destination_branch)
        self.wait_until_invisible(RepoLocators.pr_destination_branch_spinner)
        destination_branch_name_field.send_keys(Keys.ENTER)
        self.wait_until_invisible(RepoLocators.pr_branches_dropdown)
        self.wait_until_clickable(RepoLocators.pr_continue_button)
        self.wait_until_visible(RepoLocators.pr_continue_button).click()

    def submit_pull_request(self):
        self.wait_until_visible(RepoLocators.pr_description_field)
        title = self.get_element(RepoLocators.pr_title_field)
        title.clear()
        title.send_keys('Selenium test pull request')
        self.wait_until_visible(RepoLocators.pr_submit_button).click()
        self.wait_until_visible(PullRequestLocator.pull_request_activity_content)
        self.wait_until_clickable(PullRequestLocator.pull_request_page_merge_button)


class PullRequest(BasePage):

    def __init__(self, driver, project_key=None, repo_slug=None, pull_request_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug,
                                 pull_request_key=pull_request_key)
        self.page_url = url_manager.pull_request_overview()
        self.diff_url = url_manager.pull_request_diff()
        self.commits_url = url_manager.pull_request_commits()

    def wait_for_overview_tab(self):
        return self.wait_until_visible(PullRequestLocator.pull_request_activity_content)

    def go_to_overview(self):
        return self.go_to()

    def go_to_diff(self):
        self.go_to_url(url=self.diff_url)

    def go_to_commits(self):
        self.go_to_url(self.commits_url)

    def wait_for_diff_tab(self, ):
        return self.wait_until_any_element_visible(PullRequestLocator.commit_files)

    def wait_for_code_diff(self, ):
        return self.wait_until_visible(PullRequestLocator.diff_code_lines)

    def wait_for_commits_tab(self, ):
        self.wait_until_any_element_visible(PullRequestLocator.commit_message_label)

    def click_inline_comment_button_js(self):
        selector = PullRequestLocator.inline_comment_button
        self.execute_js(f"elems=document.querySelectorAll('{selector[1]}'); "
                        "item=elems[Math.floor(Math.random() * elems.length)];"
                        "item.scrollIntoView();"
                        "item.click();")

    def wait_for_comment_text_area(self):
        return self.wait_until_visible(PullRequestLocator.comment_text_area)

    def add_code_comment(self, ):
        self.wait_until_visible(PullRequestLocator.text_area).send_keys('Comment from Selenium script')
        self.click_save_comment_button()

    def click_save_comment_button(self):
        return self.wait_until_visible(PullRequestLocator.comment_button).click()

    def add_overview_comment(self):
        self.wait_for_comment_text_area().click()
        self.wait_until_clickable(PullRequestLocator.text_area).send_keys(self.generate_random_string(50))

    def wait_merge_button_clickable(self):
        self.wait_until_clickable(PullRequestLocator.pull_request_page_merge_button)

    def merge_pull_request(self):
        self.wait_until_present(PullRequestLocator.pull_request_page_merge_button).click()
        PopupManager(self.driver).dismiss_default_popup()
        self.wait_until_visible(PullRequestLocator.diagram_selector)
        self.wait_until_visible(PullRequestLocator.merge_diagram_selector)
        self.wait_until_present(PullRequestLocator.delete_branch_per_merge_checkbox)
        if self.get_element(PullRequestLocator.delete_branch_per_merge_checkbox).is_selected():
            self.execute_js(f'document.querySelector('
                            f'"{PullRequestLocator.delete_branch_per_merge_checkbox[1]}").click()')
        self.wait_until_clickable(PullRequestLocator.pull_request_modal_merge_button).click()
        self.wait_until_invisible(PullRequestLocator.del_branch_checkbox_selector)


class RepositoryBranches(BasePage):
    page_loaded_selector = BranchesLocator.branches_name

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        self.url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug)
        self.page_url = self.url_manager.repo_branches()

    def open_base_branch(self, base_branch_name):
        self.go_to_url(f"{self.url_manager.base_branch_url()}{base_branch_name}")
        self.wait_until_visible(BranchesLocator.branches_name)

    def create_branch_fork_rnd_name(self, base_branch_name):
        self.wait_until_visible(BranchesLocator.branches_action).click()
        self.get_element(BranchesLocator.branches_action_create_branch).click()
        self.wait_until_visible(BranchesLocator.new_branch_name_textfield)
        branch_name = f"{base_branch_name}-{self.generate_random_string(5)}".replace(' ', '-')
        self.get_element(BranchesLocator.new_branch_name_textfield).send_keys(branch_name)
        self.wait_until_clickable(BranchesLocator.new_branch_submit_button).click()
        return branch_name

    def delete_branch(self, branch_name):
        self.wait_until_visible(BranchesLocator.search_branch_textfield).send_keys(branch_name)
        self.wait_until_visible(BranchesLocator.branches_name)
        self.wait_until_visible(BranchesLocator.search_branch_action).click()
        self.execute_js("document.querySelector('li>a.delete-branch').click()")
        self.wait_until_clickable(BranchesLocator.delete_branch_dialog_submit).click()


class RepositorySettings(BasePage):

    def wait_repository_settings(self):
        self.wait_until_visible(RepositorySettingsLocator.repository_settings_menu)

    def delete_repository(self, repo_slug):
        self.wait_repository_settings()
        self.wait_until_visible(RepositorySettingsLocator.delete_repository_button).click()
        self.wait_until_visible(RepositorySettingsLocator.delete_repository_modal_text_field,).send_keys(repo_slug)
        self.wait_until_clickable(RepositorySettingsLocator.delete_repository_modal_submit_button)
        self.wait_until_visible(RepositorySettingsLocator.delete_repository_modal_submit_button).click()


class ForkRepositorySettings(RepositorySettings):
    def __init__(self, driver, user, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(user=user, repo_slug=repo_slug)
        self.page_url = url_manager.fork_repo_url()


class UserSettings(BasePage):

    def __init__(self, driver, user):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(user=user)
        self.page_url = url_manager.user_settings_url()

    def user_role_visible(self):
        return self.wait_until_visible(UserSettingsLocator.user_role_label)


class RepositoryCommits(BasePage):
    page_loaded_selector = RepoCommitsLocator.repo_commits_graph

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.commits_url()
