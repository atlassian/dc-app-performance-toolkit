from selenium.webdriver.common.keys import Keys
from selenium_ui.conftest import retry
import time
import random
import json

from selenium_ui.base_page import BasePage

from extension.jira.extension_selectors import UrlManager, NewProjectPageLocators, NewGoalPageLocators, ProjectSearchPageLocators, \
    GoalSearchPageLocators, ProjectDetailsPageLocators, OnboardingDialogLocators, TagSearchPageLocators

class NewProject(BasePage):
    page_loaded_selector = NewProjectPageLocators.new_project_modal_ready

    def __init__(self, driver, issue_key=None, issue_id=None):
        BasePage.__init__(self, driver)
        url_manager_modal = UrlManager()
        self.page_url = url_manager_modal.new_project_url()

    def wait_for_new_project_title(self):
        self.dismiss_popup(OnboardingDialogLocators.dismiss_onboarding_button)
        self.wait_until_visible(NewProjectPageLocators.new_project_modal_ready)

    def fill_new_project_title(self):
        text_summary = f"New project - {self.generate_random_string(10)}"
        self.wait_until_clickable(NewProjectPageLocators.new_project_name).send_keys(text_summary)

    def new_project_submit(self):
        self.get_element(NewProjectPageLocators.new_project_submit_button).click()
        self.wait_until_invisible(NewProjectPageLocators.new_project_modal_ready)

class ProjectDetails(BasePage):
    page_loaded_selector = ProjectDetailsPageLocators.project_details_header

    def __init__(self, driver):
        BasePage.__init__(self, driver)
        url_manager = UrlManager()
        self.page_url = url_manager.project_details_url()

    def wait_for_project_details(self):
        self.dismiss_popup(OnboardingDialogLocators.dismiss_onboarding_button)
        self.wait_until_visible(ProjectDetailsPageLocators.project_details_update_list)

    def fill_project_update(self):
        text_summary = f"This is the latest project update - {self.generate_random_string(50)}"
        self.get_element(ProjectDetailsPageLocators.project_update_section).click()
        # self.get_element(ProjectDetailsPageLocators.project_target_date_picker).send_keys("10/10/2028")
        # self.get_element(ProjectDetailsPageLocators.project_status_button).click()
        # self.get_element(ProjectDetailsPageLocators.project_status_on_track).click()
        # self.get_element(ProjectDetailsPageLocators.project_update_textarea).click()
        self.get_element(ProjectDetailsPageLocators.project_update_textarea).send_keys(text_summary)
        
    def create_update_submit(self):
        self.wait_until_clickable(ProjectDetailsPageLocators.create_update_button).click()


class ProjectsList(BasePage):

    def __init__(self, driver):
        BasePage.__init__(self, driver)
        url_manager = UrlManager()
        self.page_url = url_manager.project_search_url()

    def wait_for_page_loaded(self):
        self.dismiss_popup(OnboardingDialogLocators.dismiss_onboarding_button)
        self.wait_until_any_ec_presented(
            selectors=[ProjectSearchPageLocators.search_results_table])


class GoalsList(BasePage):
    def __init__(self, driver):
        BasePage.__init__(self, driver)
        url_manager = UrlManager()
        self.page_url = url_manager.goal_search_url()

    def wait_for_page_loaded(self):
        self.dismiss_popup(OnboardingDialogLocators.dismiss_onboarding_button)
        self.wait_until_any_ec_presented(
            selectors=[GoalSearchPageLocators.search_results_table])
        
class TagsList(BasePage):
    def __init__(self, driver):
        BasePage.__init__(self, driver)
        url_manager = UrlManager()
        self.page_url = url_manager.tag_search_url()

    def wait_for_page_loaded(self):
        self.dismiss_popup(OnboardingDialogLocators.dismiss_onboarding_button)
        self.wait_until_any_ec_presented(
            selectors=[TagSearchPageLocators.search_results_table])        