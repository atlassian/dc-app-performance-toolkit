from selenium.webdriver.common.by import By
from util.conf import BAMBOO_SETTINGS


class UrlManager:

    def __init__(self, builds_plan=None):
        self.host = BAMBOO_SETTINGS.server_url
        self.login_params = '/userlogin!doDefault.action?os_destination=%2FallPlans.action'
        self.logout_params = '/userLogout.action'
        self.all_projects_params = '/allProjects.action'
        self.plan_summary_params = f'/browse/{builds_plan}'
        self.plan_history_params = f'/browse/{builds_plan}/history'
        self.build_summary_params = f'/browse/{builds_plan}-1'
        self.job_configuration_params = f'/build/admin/edit/editBuildTasks.action?buildKey={builds_plan}-JB1'

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

    def job_configuration_url(self):
        return f"{self.host}{self.job_configuration_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"


class LoginPageLocators:
    login_page_url = UrlManager().login_url()
    login_button = (By.ID, "loginForm_save")
    login_username_field = (By.ID, "loginForm_os_username")
    login_password_field = (By.ID, "loginForm_os_password")


class AllProjectsLocators:
    view_all_projects_url = UrlManager().all_projects_url()
    project_table = (By.ID, "projectsTable")
    projects_button = (By.ID, "allProjects")


class AllBuildsLocators:
    all_builds_button = (By.ID, "logo")
    builds_table = (By.ID, "dashboard")


class PlanConfigurationLocators:
    edit_config_button = (By.XPATH, "//tbody/tr[1]/td[8]/a[1]/span[1]")
    config_plan_page = (By.ID, "config-sidebar")


class BuildActivityLocators:
    build_dropdown = (By.ID, "system_build_menu")
    build_activity_button = (By.XPATH, "//a[@id='currentTab']")
    build_activity_page = (By.XPATH, "//body/div[@id='page']/section[@id='content']")


class BuildLogsLocators:
    logs_button = (By.XPATH, "//strong[contains(text(),'Logs')]")
    view_logs = (By.CLASS_NAME, "log-trace")


class LogoutLocators:
    logout = (By.XPATH, "//a[@href='/userLogout.action']")
