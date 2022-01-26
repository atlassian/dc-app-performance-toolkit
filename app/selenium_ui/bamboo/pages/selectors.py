from selenium.webdriver.common.by import By
from util.conf import BAMBOO_SETTINGS


class UrlManager:

    def __init__(self, build_plan_id=None):
        self.host = BAMBOO_SETTINGS.server_url
        self.login_params = '/userlogin!doDefault.action'
        self.logout_params = '/userLogout.action'
        self.all_projects_params = '/allProjects.action'
        self.plan_summary_params = f'/browse/{build_plan_id}'
        self.plan_history_params = f'/browse/{build_plan_id}/history'
        self.build_summary_params = f'/browse/{build_plan_id}-1'

    def login_url(self):
        return f"{self.host}{self.login_params}"

    def all_projects_url(self):
        return f"{self.host}{self.all_projects_params}"

    def plan_summary_url(self):
        return f"{self.host}{self.plan_summary_params}"

    def plan_history_url(self):
        return f"{self.host}{self.plan_history_params}"

    def build_summary_url(self):
        return f"{self.host}{self.build_summary_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"


class LoginPageLocators:
    login_page_url = UrlManager().login_url()
    login_username_field = (By.ID, "loginForm_os_username")
    login_password_field = (By.ID, "loginForm_os_password")
    login_submit_button = (By.ID, "loginForm_save")


class AllProjectsLocators:
    view_all_projects_url = UrlManager().all_projects_url()
    project_table = (By.ID, "projectsTable")
    project_name_column = (By.ID, "projectsTable")
    projects_button = (By.ID, "allProjects")


class AllBuildsLocators:
    all_builds_button = (By.ID, "logo")
    builds_table = (By.ID, "dashboard")


class PlanConfigurationLocators:
    edit_config_button = (By.XPATH, "//span[contains(text(),'Configure plan')]")
    config_plan_page = (By.ID, "config-sidebar")
    config_plan_page_content = (By.ID, "content")


class BuildActivityLocators:
    build_dropdown = (By.ID, "system_build_menu")
    build_activity_button = (By.ID, "currentTab")
    build_activity_page = (By.ID, "page")
    build_dashboard = (By.ID, "dashboard-instance-name")


class PlanSummaryLocators:
    plan_details_summary = (By.ID, "planDetailsSummary")
    plan_stats_summary = (By.ID, "planStatsSummary")


class PlanHistoryLocators:
    build_results = (By.CLASS_NAME, "aui-page-panel-content")


class BuildSummaryLocators:
    build_summary_status = (By.ID, "status-ribbon")


class BuildLogsLocators:
    logs_button = (By.XPATH, "//strong[contains(text(),'Logs')]")
    view_logs = (By.CLASS_NAME, "log-trace")


class JobConfigLocators:
    edit_panel = (By.ID, "panel-editor-setup")
    edit_panel_list = (By.ID, "panel-editor-list")
    job_config = (By.CLASS_NAME, "job")


class LogoutLocators:
    logout_url = UrlManager().logout_url()
    login_button_link = (By.ID, "login")
