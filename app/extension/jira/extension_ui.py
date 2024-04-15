import random

from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login
from extension.jira.extenstion_pages import NewProject, ProjectDetails, ProjectsList, GoalsList, TagsList
from util.conf import JIRA_SETTINGS


def jps_view_projects(webdriver, datasets):
    page = BasePage(webdriver)

    # To run action as specific user uncomment code bellow.
    # NOTE: If app_specific_action is running as specific user, make sure that app_specific_action is running
    # just before test_2_selenium_z_log_out action
    #
    # @print_timing("selenium_app_specific_user_login")
    # def measure():
    #     def app_specific_user_login(username='admin', password='admin'):
    #         login_page = Login(webdriver)
    #         login_page.delete_all_cookies()
    #         login_page.go_to()
    #         login_page.set_credentials(username=username, password=password)
    #         if login_page.is_first_login():
    #             login_page.first_login_setup()
    #         if login_page.is_first_login_second_page():
    #             login_page.first_login_second_page_setup()
    #         login_page.wait_for_page_loaded()
    #     app_specific_user_login(username='admin', password='admin')
    # measure()

    project_list_page = ProjectsList(webdriver)

    @print_timing("selenium_jps_view_projects_action")
    def measure():
        project_list_page.go_to()
        project_list_page.wait_for_page_loaded()

    measure()

def jps_view_goals(webdriver, datasets):
    page = BasePage(webdriver)

    goal_list_page = GoalsList(webdriver)

    @print_timing("selenium_jps_view_goals_action")
    def measure():
        goal_list_page.go_to()
        goal_list_page.wait_for_page_loaded()

    measure()    

def jps_view_tags(webdriver, datasets):
    page = BasePage(webdriver)

    tag_list_page = TagsList(webdriver)

    @print_timing("selenium_jps_view_tags_action")
    def measure():
        tag_list_page.go_to()
        tag_list_page.wait_for_page_loaded()

    measure()  

def jps_create_project(webdriver, datasets):
    page = BasePage(webdriver)

    new_project_page = NewProject(webdriver)

    @print_timing("selenium_jps_create_projects_action")
    def measure():
        new_project_page.go_to()
        new_project_page.wait_for_new_project_title()
        new_project_page.fill_new_project_title()
        new_project_page.new_project_submit()

    measure()

def jps_create_project_update(webdriver, datasets):
    page = BasePage(webdriver)

    project_details_page = ProjectDetails(webdriver)

    @print_timing("selenium_jps_create_project_update_action")
    def measure():
        project_details_page.go_to()
        project_details_page.wait_for_project_details()
        project_details_page.fill_project_update()
        project_details_page.create_update_submit()

    measure()    