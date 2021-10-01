from selenium_ui.base_page import BasePage

from selenium_ui.bamboo.pages.selectors import UrlManager, LoginPageLocators, AllProjectsLocators, AllBuildsLocators, \
    PlanConfigurationLocators, BuildActivityLocators, PlanSummaryLocators, PlanHistoryLocators, BuildSummaryLocators, \
    BuildLogsLocators, JobConfigLocators


class Login(BasePage):
    page_url = LoginPageLocators.login_page_url

    def click_login_button(self):
        self.wait_until_visible(LoginPageLocators.login_button).click()
        self.wait_until_invisible(LoginPageLocators.login_button)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_username_field).send_keys(username)
        self.get_element(LoginPageLocators.login_password_field).send_keys(password)


class ProjectList(BasePage):
    page_loaded_selector = [AllProjectsLocators.project_table, AllProjectsLocators.project_name_column]

    def click_projects_button(self):
        self.wait_until_visible(AllProjectsLocators.projects_button).click()


class BuildList(BasePage):
    page_loaded_selector = AllBuildsLocators.builds_table

    def click_all_builds_button(self):
        self.wait_until_visible(AllBuildsLocators.all_builds_button).click()


class PlanConfiguration(BasePage):
    page_loaded_selector = [PlanConfigurationLocators.config_plan_page,
                            PlanConfigurationLocators.config_plan_page_content]

    def click_config_plan_button(self):
        self.wait_until_visible(PlanConfigurationLocators.edit_config_button).click()


class BuildActivity(BasePage):
    page_loaded_selector = [BuildActivityLocators.build_activity_page, BuildActivityLocators.build_dashboard]

    def open_build_dropdown(self):
        self.wait_until_clickable(BuildActivityLocators.build_dropdown).click()
        self.wait_until_clickable(BuildActivityLocators.build_activity_button).click()


class PlanSummary(BasePage):
    page_loaded_selector = [PlanSummaryLocators.plan_details_summary, PlanSummaryLocators.plan_stats_summary]

    def __init__(self, driver, build_plan_id=None):
        BasePage.__init__(self, driver)
        plan_summary = UrlManager(build_plan_id=build_plan_id)
        self.plan_summary_url = plan_summary.plan_summary_url()

    def go_to_summary_plan_page(self):
        self.go_to_url(self.plan_summary_url)


class PlanHistory(BasePage):
    page_loaded_selector = PlanHistoryLocators.build_results

    def __init__(self, driver, build_plan_id=None):
        BasePage.__init__(self, driver)
        plan_history = UrlManager(build_plan_id=build_plan_id)
        self.plan_history_url = plan_history.plan_history_url()

    def go_to_plan_history_page(self):
        self.go_to_url(self.plan_history_url)


class BuildSummary(BasePage):
    page_loaded_selector = BuildSummaryLocators.build_summary_status

    def __init__(self, driver, build_plan_id=None):
        BasePage.__init__(self, driver)
        build_summary = UrlManager(build_plan_id=build_plan_id)
        self.build_summary_url = build_summary.build_summary_url()

    def go_to_build_summary_page(self):
        self.go_to_url(self.build_summary_url)


class BuildLogs(BasePage):
    page_loaded_selector = BuildLogsLocators.view_logs

    def go_to_build_logs(self):
        self.wait_until_clickable(BuildLogsLocators.logs_button).click()


class JobConfiguration(BasePage):
    page_loaded_selector = [JobConfigLocators.edit_panel, JobConfigLocators.edit_panel]

    def click_config_plan_button(self):
        self.wait_until_clickable(AllBuildsLocators.all_builds_button).click()
        self.wait_until_visible(PlanConfigurationLocators.edit_config_button).click()

    def click_job_config_button(self):
        self.wait_until_clickable(JobConfigLocators.job_config).click()


class Logout(BasePage):
    UrlManager().logout_url()
