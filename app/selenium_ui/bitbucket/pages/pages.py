from packaging import version

from selenium_ui.base_page import BasePage
from selenium_ui.bitbucket.pages.selectors import LoginPageLocators, GetStartedLocators, \
    DashboardLocators, ProjectsLocators, ProjectLocators, RepoLocators, RepoNavigationPanelLocators, PopupLocators, \
    PullRequestLocator, BranchesLocator, RepoCommitsLocator, LogoutPageLocators, UrlManager, AdminLocators


class LoginPage(BasePage):
    page_url = UrlManager().login_url()
    page_loaded_selector = LoginPageLocators.footer_panel

    def __init__(self, driver):
        super().__init__(driver)
        self.is_2sv_login = False

    def wait_for_page_loaded(self):
        self.wait_until_visible(LoginPageLocators.footer_panel)
        if not self.get_elements(LoginPageLocators.submit_button):
            self.is_2sv_login = True
            print("INFO: 2sv login form")


    def fill_username(self, username):
        self.get_element(LoginPageLocators.username_textfield).send_keys(username)

    def fill_2sv_username(self, username):
        self.wait_until_visible(LoginPageLocators.login_username_field_2sv)
        self.get_element(LoginPageLocators.login_username_field_2sv).send_keys(username)

    def fill_2sv_password(self, username):
        self.wait_until_visible(LoginPageLocators.login_username_field_2sv)
        self.get_element(LoginPageLocators.login_password_field_2sv).send_keys(username)

    def fill_password(self, password):
        self.get_element(LoginPageLocators.password_textfield).send_keys(password)

    def submit_login(self):
        if self.is_2sv_login:
            self.wait_until_visible(LoginPageLocators.login_button_2sv).click()
        else:
            self.wait_until_visible(LoginPageLocators.submit_button).click()

    def set_credentials(self, username, password):
        if self.is_2sv_login:
            self.fill_2sv_username(username)
            self.fill_2sv_password(password)
        else:
            self.fill_username(username)
            self.fill_password(password)

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

    def close_whats_new_window(self):
        popup_window = self.get_elements(GetStartedLocators.whats_new_window_close_button)
        if popup_window:
            self.wait_until_visible(GetStartedLocators.whats_new_window_close_button).click()
            self.wait_until_invisible(GetStartedLocators.whats_new_window_close_button)


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

    def wait_for_navigation_panel(self):
        return self.wait_until_present(RepoNavigationPanelLocators.navigation_panel)


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.popup_selectors)


class Repository(BasePage):

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.repo_url()
        self.repo_slug = repo_slug
        self.project_key = project_key


class RepoPullRequests(BasePage):
    page_loaded_selector = RepoLocators.pull_requests_list

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        self.url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug)
        self.page_url = self.url_manager.repo_pull_requests()

    def create_new_pull_request(self, from_branch, to_branch):
        self.go_to_url(url=self.url_manager.create_pull_request_url(from_branch=from_branch,
                                                                    to_branch=to_branch))
        if self.app_version > version.parse("8.0.0"):
            self.wait_until_clickable(self.get_selector(RepoLocators.pr_continue_button))
            self.wait_until_visible(self.get_selector(RepoLocators.pr_continue_button)).click()
        self.submit_pull_request()

    def submit_pull_request(self):
        self.wait_until_visible(self.get_selector(RepoLocators.pr_description_field))
        title = self.get_element(self.get_selector(RepoLocators.pr_title_field))
        title.clear()
        title.send_keys('Selenium test pull request')
        self.wait_until_visible(self.get_selector(RepoLocators.pr_submit_button)).click()
        self.wait_until_visible(PullRequestLocator.pull_request_activity_content)
        updates_banners = self.get_elements(PullRequestLocator.updates_info_banner)
        while updates_banners:
            updates_banners[0].click()
            self.driver.refresh()
            updates_banners = self.get_elements(PullRequestLocator.updates_info_banner)
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

    def dismiss_updates_info_popup(self):
        updates_banners = self.get_elements(PullRequestLocator.updates_info_banner)
        while updates_banners:
            updates_banners[0].click()
            self.driver.refresh()
            updates_banners = self.get_elements(PullRequestLocator.updates_info_banner)

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


class RepositoryCommits(BasePage):
    page_loaded_selector = RepoCommitsLocator.repo_commits_graph

    def __init__(self, driver, project_key, repo_slug):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, repo_slug=repo_slug)
        self.page_url = url_manager.commits_url()


class AdminPage(BasePage):
    page_url = AdminLocators.admin_system_page_url
    page_loaded_selector = AdminLocators.login_form

    def is_websudo(self):
        return True if self.get_elements(AdminLocators.web_sudo_password) else False

    def do_websudo(self, password):
        self.wait_until_clickable(AdminLocators.web_sudo_password).send_keys(password)
        self.wait_until_clickable(AdminLocators.web_sudo_submit_btn).click()
        self.wait_until_visible(AdminLocators.administration_link)

    def go_to(self, password=None):
        super().go_to()
        self.wait_for_page_loaded()
        if self.is_websudo():
            self.do_websudo(password)