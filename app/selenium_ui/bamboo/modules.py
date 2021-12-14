import random

from selenium_ui.bamboo.pages.pages import Login, Logout, ProjectList, BuildList, PlanConfiguration, BuildActivity, \
    PlanSummary, BuildSummary, BuildLogs, PlanHistory, JobConfiguration
from selenium_ui.conftest import print_timing

USERS = "users"
BUILD_PLANS = "build_plans"


def setup_run_data(datasets):
    user = random.choice(datasets[USERS])
    build_plan = random.choice(datasets[BUILD_PLANS])
    datasets['username'] = user[0]
    datasets['password'] = user[1]
    datasets['build_plan_id'] = build_plan[1]


def login(webdriver, datasets):
    setup_run_data(datasets)
    login_page = Login(webdriver)

    @print_timing("selenium_login")
    def measure():
        @print_timing("selenium_login:open_login_page")
        def sub_measure():
            login_page.go_to()

        sub_measure()

        login_page.set_credentials(username=datasets['username'], password=datasets['password'])
        login_page.click_login_button()

    measure()


def view_all_projects(webdriver, datasets):
    @print_timing("selenium_view_all_projects")
    def measure():
        projects_page = ProjectList(webdriver)
        projects_page.click_projects_button()
        projects_page.wait_for_page_loaded()
    measure()


def view_all_builds(webdriver, datasets):
    @print_timing("selenium_view_all_builds")
    def measure():
        builds_page = BuildList(webdriver)
        builds_page.click_all_builds_button()
        builds_page.wait_for_page_loaded()

    measure()


def config_plan(webdriver, datasets):
    @print_timing("selenium_config_plan")
    def measure():
        config_page = PlanConfiguration(webdriver)
        config_page.click_config_plan_button()
        config_page.wait_for_page_loaded()

    measure()


def builds_queue_page(webdriver, datasets):
    @print_timing("selenium_view_build_activity")
    def measure():
        activity_page = BuildActivity(webdriver)
        activity_page.open_build_dropdown()
        activity_page.wait_for_page_loaded()

    measure()


def view_plan_summary(webdriver, datasets):
    plan_summary = PlanSummary(webdriver, build_plan_id=datasets['build_plan_id'])

    @print_timing("selenium_view_plan_summary")
    def measure():
        plan_summary.go_to_summary_plan_page()
        plan_summary.wait_for_page_loaded()

    measure()


def view_build_summary(webdriver, datasets):
    build_summary = BuildSummary(webdriver, build_plan_id=datasets['build_plan_id'])

    @print_timing("selenium_view_build_summary")
    def measure():
        build_summary.go_to_build_summary_page()
        build_summary.wait_for_page_loaded()

    measure()


def view_plan_history_page(webdriver, datasets):
    plan_history = PlanHistory(webdriver, build_plan_id=datasets['build_plan_id'])

    @print_timing("selenium_view_plan_history")
    def measure():
        plan_history.go_to_plan_history_page()
        plan_history.wait_for_page_loaded()

    measure()


def view_build_logs(webdriver, datasets):
    @print_timing("selenium_view_build_logs")
    def measure():
        view_logs = BuildLogs(webdriver)
        view_logs.go_to_build_logs()
        view_logs.wait_for_page_loaded()

    measure()


def view_job_configuration(webdriver, datasets):

    @print_timing("selenium_view_job_configuration")
    def measure():
        view_job_configuration_page = JobConfiguration(webdriver)
        view_job_configuration_page.click_config_plan_button()
        view_job_configuration_page.click_job_config_button()
        view_job_configuration_page.wait_for_page_loaded()
    measure()


def log_out(webdriver, datasets):
    @print_timing("selenium_log_out")
    def measure():
        Logout(webdriver)

    measure()
