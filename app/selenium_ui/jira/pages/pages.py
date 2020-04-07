from selenium.webdriver.common.keys import Keys
import time
import random

from selenium_ui.base_page import BasePage
from selenium_ui.jira.pages.selectors import UrlManager, LoginPageLocators, DashboardLocators, PopupLocators, \
    IssueLocators, ProjectLocators, SearchLocators, BoardsListLocators, BoardLocators, LogoutLocators


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.default_popup, PopupLocators.popup_1, PopupLocators.popup_2)


class Login(BasePage):
    page_url = LoginPageLocators.login_url
    page_loaded_selector = LoginPageLocators.system_dashboard

    def is_first_login(self):
        return True if self.get_elements(LoginPageLocators.continue_button) else False

    def first_login_setup(self, interaction):
        self.wait_until_visible(LoginPageLocators.continue_button, interaction).send_keys(Keys.ESCAPE)
        self.get_element(LoginPageLocators.continue_button).click()
        self.wait_until_visible(LoginPageLocators.avatar_page_next_button, interaction).click()
        self.wait_until_visible(LoginPageLocators.explore_current_projects, interaction).click()
        self.go_to_url(DashboardLocators.dashboard_url)
        self.wait_until_visible(DashboardLocators.dashboard_window, interaction)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()


class Logout(BasePage):
    page_url = LogoutLocators.logout_url

    def click_logout(self):
        self.get_element(LogoutLocators.logout_submit_button).click()

    def wait_for_page_loaded(self, interaction):
        self.wait_until_present(LogoutLocators.login_button_link, interaction)


class Dashboard(BasePage):
    page_url = DashboardLocators.dashboard_url

    def wait_dashboard_presented(self, interaction):
        self.wait_until_present(DashboardLocators.dashboard_window, interaction)


class Issue(BasePage):
    page_loaded_selector = IssueLocators.issue_title

    def __init__(self, driver, issue_key=None, issue_id=None):
        BasePage.__init__(self, driver)
        url_manager_modal = UrlManager(issue_key=issue_key)
        url_manager_edit_page = UrlManager(issue_id=issue_id)
        self.page_url = url_manager_modal.issue_url()
        self.page_url_edit_issue = url_manager_edit_page.edit_issue_url()
        self.page_url_edit_comment = url_manager_edit_page.edit_comments_url()

    def wait_for_issue_title(self, interaction):
        self.wait_until_visible(IssueLocators.issue_title, interaction)

    def go_to_edit_issue(self, interaction):
        self.go_to_url(self.page_url_edit_issue)
        self.wait_until_visible(IssueLocators.edit_issue_page, interaction)

    def go_to_edit_comment(self, interaction):
        self.go_to_url(self.page_url_edit_comment)
        self.wait_until_visible(IssueLocators.edit_comment_add_comment_button, interaction)

    def fill_summary_edit(self):
        text_summary = f"Edit summary form selenium - {self.generate_random_string(10)}"
        self.get_element(IssueLocators.issue_summary_field).send_keys(text_summary)

    def __fill_rich_editor_textfield(self, text, interaction, selector):
        self.wait_until_available_to_switch(selector, interaction)
        self.get_element(IssueLocators.tinymce_description_field).send_keys(text)
        self.return_to_parent_frame()

    def edit_issue_submit(self):
        self.get_element(IssueLocators.edit_issue_submit).click()

    def fill_description_edit(self, interaction):
        text_description = f"Edit description form selenium - {self.generate_random_string(30)}"
        self.__fill_rich_editor_textfield(text_description, interaction, selector=IssueLocators.issue_description_field)

    def open_create_issue_modal(self, interaction):
        self.wait_until_clickable(IssueLocators.create_issue_button, interaction).click()
        self.wait_until_visible(IssueLocators.issue_modal, interaction)

    def fill_description_create(self, interaction):
        text_description = f'Description: {self.generate_random_string(100)}'
        self.__fill_rich_editor_textfield(text_description, interaction, selector=IssueLocators.issue_description_field)

    def fill_summary_create(self, interaction):
        summary = f"Issue created date {time.time()}"
        self.wait_until_clickable(IssueLocators.issue_summary_field, interaction).send_keys(summary)

    def assign_to_me(self):
        assign_to_me_links = self.get_elements(IssueLocators.issue_assign_to_me_link)
        for link in assign_to_me_links:
            link.click()

    def set_resolution(self):
        resolution_field = self.get_elements(IssueLocators.issue_resolution_field)
        if resolution_field:
            dropdown_length = len(self.select(resolution_field[0]).options)
            random_resolution_id = random.randint(1, dropdown_length - 1)
            self.select(resolution_field[0]).select_by_index(random_resolution_id)

    def set_issue_type(self, interaction):
        def __filer_epic(element):
            return "epic" not in element.get_attribute("class").lower()

        self.get_element(IssueLocators.issue_type_field).click()
        issue_dropdown_elements = self.get_elements(IssueLocators.issue_type_dropdown_elements)
        if issue_dropdown_elements:
            filtered_issue_elements = list(filter(__filer_epic, issue_dropdown_elements))
            rnd_issue_type_el = random.choice(filtered_issue_elements)
            self.action_chains().move_to_element(rnd_issue_type_el).click(rnd_issue_type_el).perform()
        self.wait_until_invisible(IssueLocators.issue_ready_to_save_spinner, interaction)

    def submit_issue(self, interaction):
        self.wait_until_clickable(IssueLocators.issue_submit_button, interaction).click()
        self.wait_until_invisible(IssueLocators.issue_modal)

    def fill_comment_edit(self, interaction):
        text = 'Comment from selenium'
        self.__fill_rich_editor_textfield(text, interaction, selector=IssueLocators.edit_comment_text_field)

    def edit_comment_submit(self, interaction):
        self.get_element(IssueLocators.edit_comment_add_comment_button).click()
        self.wait_until_visible(IssueLocators.issue_title)


class Project(BasePage):
    page_loaded_selector = ProjectLocators.project_summary_property_column

    def __init__(self, driver, project_key):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.project_summary_url()


class ProjectsList(BasePage):

    def __init__(self, driver, projects_list_pages):
        BasePage.__init__(self, driver)
        self.projects_list_page = random.randint(1, projects_list_pages)
        url_manager = UrlManager(projects_list_page=self.projects_list_page)
        self.page_url = url_manager.projects_list_page_url()

    def wait_for_page_loaded(self, interaction):
        self.wait_until_any_ec_presented(selector_names=[ProjectLocators.projects_list,
                                                         ProjectLocators.projects_not_found],
                                         interaction=interaction)


class BoardsList(BasePage):
    page_url = BoardsListLocators.boards_list_url
    page_loaded_selector = BoardsListLocators.boards_list


class Search(BasePage):

    def __init__(self, driver, jql):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(jql=jql)
        self.page_url = url_manager.jql_search_url()

    def wait_for_page_loaded(self, interaction):
        self.wait_until_any_ec_presented(selector_names=[SearchLocators.search_issue_table,
                                                         SearchLocators.search_issue_content,
                                                         SearchLocators.search_no_issue_found],
                                         interaction=interaction)


class Board(BasePage):
    page_loaded_selector = BoardLocators.board_columns

    def __init__(self, driver, board_id):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(board_id=board_id)
        self.page_url = url_manager.scrum_board_url()
        self.backlog_url = url_manager.scrum_board_backlog_url()

    def go_to_backlog(self):
        self.go_to_url(self.backlog_url)

    def wait_for_scrum_board_backlog(self, interaction):
        self.wait_until_present(BoardLocators.scrum_board_backlog_content, interaction)
