from selenium.webdriver.common.by import By
from util.conf import JIRA_SETTINGS

class UrlManager:
    def __init__(self, project_id=None, projects_list_page=None, goals_list_page=None):
        self.host = JIRA_SETTINGS.server_url
        self.new_project = '/plugins/servlet/ps/configuration?modal=new-project'
        self.new_goal = '/plugins/servlet/ps/project-search&modal=new-goal'
        self.project_search = '/plugins/servlet/ps/project-search'
        self.tag_search = '/plugins/servlet/ps/tag-search'
        self.goal_search = '/plugins/servlet/ps/goal-search'
        self.project_details = '/plugins/servlet/ps/project-details/2'

    def new_project_url(self):
        return f"{self.host}{self.new_project}"

    def new_goal_url(self):
        return f"{self.host}{self.new_goal}"

    def project_search_url(self):
        return f"{self.host}{self.project_search}"

    def tag_search_url(self):
        return f"{self.host}{self.tag_search}"

    def goal_search_url(self):
        return f"{self.host}{self.goal_search}"

    def project_details_url(self):
        return f"{self.host}{self.project_details}"

class NewProjectPageLocators:
    new_project_url = UrlManager().new_project_url()
    new_project_modal_ready = (By.ID, 'create-project-button')
    new_project_name = (By.ID, 'name')
    new_project_submit_button = (By.ID, "create-project-button")
    new_project_cancel_button = (By.ID, "create-project-cancel-button")

class NewGoalPageLocators:
    new_goal_url = UrlManager().new_goal_url()
    new_project_modal_ready = (By.ID, 'name-label')
    new_goal_name = (By.ID, 'name')
    new_goal_target_date = (By.ID, 'goal-target-date')
    new_goal_submit_button = (By.ID, "create-new-goal")
    new_goal_cancel_button = (By.ID, "new-goal-cancel")

class ProjectSearchPageLocators:
    project_search_url = UrlManager().project_search_url()
    search_project_name = (By.ID, "search-project-name")
    search_results_table = (By.CLASS_NAME, "table-tree-search-results")

class TagSearchPageLocators:
    tag_search_url = UrlManager().tag_search_url()
    search_project_name = (By.ID, "search-tag-name")
    search_results_table = (By.CLASS_NAME, "table-tree-search-results")    

class GoalSearchPageLocators:
    goal_search_url = UrlManager().goal_search_url()
    search_project_name = (By.ID, "search-goal-name")
    search_results_table = (By.CLASS_NAME, "table-tree-search-results")

class ProjectDetailsPageLocators:
    project_details_url = UrlManager().project_details_url()
    project_details_update_list = (By.ID, 'project-details-update-card-list')
    project_details_history = (By.CLASS_NAME, 'timeline-container')
    project_details_header = (By.ID, 'project-details-header')
    create_update_button = (By.ID, "create-update-button")
    cancel_update_button = (By.ID, "cancel-update-button")
    project_update_section = (By.CLASS_NAME, "update-textarea")
    project_update_textarea = (By.ID, "project-update-textarea")
    project_target_date_picker = (By.ID, "project-target-date-picker")
    project_status_button = (By.ID, "project-status-update-select-button")
    project_status_on_track = (By.ID, "react-select-8-option-3")

class OnboardingDialogLocators:
    onboarding_popup = '#onboarding-project-general'
    next_onboarding_button = "#next-onboarding-stage"
    previous_onboarding_button = "#previous-onboarding-stage"
    dismiss_onboarding_button = "#dismiss-general-onboarding"
