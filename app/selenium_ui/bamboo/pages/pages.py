from selenium_ui.base_page import BasePage

from selenium_ui.bamboo.pages.selectors import UrlManager, LoginPageLocators, AllProjectsLocators, AllBuildsLocators, \
    PlanConfigurationLocators, BuildActivityLocators, BuildLogsLocators


class Login(BasePage):
    page_url = LoginPageLocators.login_page_url

    def click_login_button(self):
        self.wait_until_visible(LoginPageLocators.login_button).click()
        self.wait_until_invisible(LoginPageLocators.login_button)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_username_field).send_keys(username)
        self.get_element(LoginPageLocators.login_password_field).send_keys(password)


class ProjectList(BasePage):

    def click_projects_button(self):
        self.wait_until_visible(AllProjectsLocators.projects_button).click()

    def view_all_projects(self):
        self.wait_until_visible(AllProjectsLocators.project_table)


class BuildList(BasePage):

    def click_all_builds_button(self):
        self.wait_until_visible(AllBuildsLocators.all_builds_button).click()

    def view_all_builds(self):
        self.wait_until_visible(AllBuildsLocators.builds_table)


class PlanConfiguration(BasePage):

    def click_config_plan_button(self):
        self.wait_until_visible(PlanConfigurationLocators.edit_config_button).click()

    def config_plan_page(self):
        self.wait_until_visible(PlanConfigurationLocators.config_plan_page)


class BuildActivity(BasePage):

    def open_build_dropdown(self):
        self.wait_until_clickable(BuildActivityLocators.build_dropdown).click()
        self.wait_until_clickable(BuildActivityLocators.build_activity_button).click()

    def build_activity_page(self):
        self.wait_until_visible(BuildActivityLocators.build_activity_page)


class PlanSummary(BasePage):

    def __init__(self, driver, build_plans=None):
        BasePage.__init__(self, driver)
        plan_summary = UrlManager(builds_plan=build_plans)
        self.plan_summary_url = plan_summary.plan_summary_url()

    def view_summary_plan(self):
        self.go_to_url(self.plan_summary_url)


class PlanHistory(BasePage):

    def __init__(self, driver, build_plans=None):
        BasePage.__init__(self, driver)
        plan_history = UrlManager(builds_plan=build_plans)
        self.plan_history_url = plan_history.plan_history_url()

    def view_plan_history(self):
        self.go_to_url(self.plan_history_url)


class BuildSummary(BasePage):

    def __init__(self, driver, build_plans=None):
        BasePage.__init__(self, driver)
        build_summary = UrlManager(builds_plan=build_plans)
        self.build_summary_url = build_summary.build_summary_url()

    def view_build_summary_page(self):
        self.go_to_url(self.build_summary_url)


class BuildLogs(BasePage):

    def view_build_logs(self):
        self.wait_until_clickable(BuildLogsLocators.logs_button).click()
        self.wait_until_visible(BuildLogsLocators.view_logs)


class JobConfiguration(BasePage):

    def __init__(self, driver, build_plans=None):
        BasePage.__init__(self, driver)
        job_config = UrlManager(builds_plan=build_plans)
        self.job_config_url = job_config.job_configuration_url()

    def job_configuration_page(self):
        self.go_to_url(self.job_config_url)


class Logout(BasePage):
    UrlManager().logout_url()
