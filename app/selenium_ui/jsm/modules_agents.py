from selenium_ui.conftest import print_timing
from selenium_ui.jsm.pages.agent_pages import Login, PopupManager, Logout, BrowseProjects, BrowseCustomers, \
    ViewCustomerRequest, ViewQueue, Report
import random

from util.api.jira_clients import JiraRestClient
from util.conf import JSM_SETTINGS

client = JiraRestClient(JSM_SETTINGS.server_url, JSM_SETTINGS.admin_login, JSM_SETTINGS.admin_password)
rte_status = client.check_rte_status()

REQUESTS = "requests"
AGENTS = "agents"
REPORTS = 'reports'
SERVICE_DESKS_LARGE = "service_desks_large"
SERVICE_DESKS_SMALL = "service_desks_small"
SERVICE_DESKS_MEDIUM = "service_desks_medium"


def setup_run_data(datasets):
    agent = random.choice(datasets[AGENTS])
    request = random.choice(datasets[REQUESTS])

    if datasets[SERVICE_DESKS_LARGE]:
        service_desk_large = random.choice(datasets[SERVICE_DESKS_LARGE])
        datasets['large_project_id'] = service_desk_large[1]
        datasets['large_project_key'] = service_desk_large[2]
        datasets['all_open_queue_id_large'] = service_desk_large[4]

    if datasets[SERVICE_DESKS_MEDIUM]:
        service_desk_medium = random.choice(datasets[SERVICE_DESKS_MEDIUM])
        datasets['medium_project_id'] = service_desk_medium[1]
        datasets['medium_project_key'] = service_desk_medium[2]
        datasets['all_open_queue_id_medium'] = service_desk_medium[4]

        # Medium projects reports
        service_desk_medium_key = service_desk_medium[2]
        for report in datasets[REPORTS]:
            if service_desk_medium_key in report:
                datasets['m_report_service_desk_id'] = report[0]
                datasets['m_report_service_desk_key'] = report[1]
                datasets['m_report_created_vs_resolved_id'] = report[2]
                datasets['m_report_time_to_resolution_id'] = report[3]

    if datasets[SERVICE_DESKS_SMALL]:
        service_desk_small = random.choice(datasets[SERVICE_DESKS_SMALL])
        datasets['small_project_id'] = service_desk_small[1]
        datasets['small_project_key'] = service_desk_small[2]
        datasets['all_open_queue_id_small'] = service_desk_small[4]

        # Small projects reports
        service_desk_small_key = service_desk_small[2]
        for report in datasets[REPORTS]:
            if service_desk_small_key in report:
                datasets['s_report_service_desk_id'] = report[0]
                datasets['s_report_service_desk_key'] = report[1]
                datasets['s_report_created_vs_resolved_id'] = report[2]
                datasets['s_report_time_to_resolution_id'] = report[3]

    # Prepare random project key
    service_desk_random = random.choice(datasets[SERVICE_DESKS_SMALL] + datasets[SERVICE_DESKS_MEDIUM]
                                        + datasets[SERVICE_DESKS_LARGE])
    datasets['random_project_key'] = service_desk_random[2]

    # Define users dataset
    datasets['agent_username'] = agent[0]
    datasets['agent_password'] = agent[1]

    # Define request dataset
    datasets['request_id'] = request[0]
    datasets['request_key'] = request[1]


def login(webdriver, datasets):
    setup_run_data(datasets)

    @print_timing("selenium_agent_login")
    def measure():
        login_page = Login(webdriver)

        @print_timing("selenium_agent_login:open_login_page")
        def sub_measure():
            login_page.go_to()
        sub_measure()

        @print_timing("selenium_agent_login:login_and_view_dashboard")
        def sub_measure():
            login_page.set_credentials(username=datasets['agent_username'], password=datasets['agent_password'])
            if login_page.is_first_login():
                login_page.first_login_setup()
            login_page.wait_for_page_loaded()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_workload_report_medium(webdriver, datasets):
    workload_report = Report.view_workload_report(webdriver, project_key=datasets['m_report_service_desk_key'])

    @print_timing('selenium_agent_view_workload_report_medium')
    def measure():
        workload_report.go_to()
        workload_report.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_time_to_resolution_report_medium(webdriver, datasets):
    time_to_resolution_report = Report.view_time_to_resolution_report(webdriver, project_key=
                                                                      datasets['m_report_service_desk_key'],
                                                                      time_to_resolution_report_id=
                                                                      datasets['m_report_time_to_resolution_id'])

    @print_timing('selenium_agent_view_time_to_resolution_medium')
    def measure():
        time_to_resolution_report.go_to()
        time_to_resolution_report.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_created_vs_resolved_report_medium(webdriver, datasets):
    created_vs_resolved = Report.view_created_vs_resolved_report(webdriver, project_key=
                                                                 datasets['m_report_service_desk_key'],
                                                                 created_vs_resolved_report_id=
                                                                 datasets['m_report_created_vs_resolved_id'])

    @print_timing('selenium_agent_created_vs_resolved_report_medium')
    def measure():
        created_vs_resolved.go_to()
        created_vs_resolved.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_workload_report_small(webdriver, datasets):
    workload_report = Report.view_workload_report(webdriver, project_key=datasets['s_report_service_desk_key'])

    @print_timing('selenium_agent_view_workload_report_small')
    def measure():
        workload_report.go_to()
        workload_report.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_time_to_resolution_report_small(webdriver, datasets):
    time_to_resolution_report = Report.view_time_to_resolution_report(webdriver, project_key=
                                                                      datasets['s_report_service_desk_key'],
                                                                      time_to_resolution_report_id=
                                                                      datasets['s_report_time_to_resolution_id'])

    @print_timing('selenium_agent_view_time_to_resolution_small')
    def measure():
        time_to_resolution_report.go_to()
        time_to_resolution_report.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_created_vs_resolved_report_small(webdriver, datasets):
    created_vs_resolved = Report.view_created_vs_resolved_report(webdriver, project_key=
                                                                 datasets['s_report_service_desk_key'],
                                                                 created_vs_resolved_report_id=
                                                                 datasets['s_report_created_vs_resolved_id'])

    @print_timing('selenium_agent_created_vs_resolved_report_small')
    def measure():
        created_vs_resolved.go_to()
        created_vs_resolved.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_queue_form_diff_projects_size(browse_queue_page, project_size):
    @print_timing(f'selenium_agent_{project_size}_project_view_queue')
    def measure():
        @print_timing(f'selenium_agent_{project_size}_project_view_queue:all_open')
        def sub_measure():
            browse_queue_page.go_to()
            browse_queue_page.wait_for_page_loaded()
        sub_measure()

        @print_timing(f'selenium_agent_{project_size}_project_view_queue:random_choice_queue')
        def sub_measure():
            browse_queue_page.get_random_queue()
        sub_measure()
    measure()


def browse_projects_list(webdriver, datasets):
    browse_projects_page = BrowseProjects(webdriver)

    @print_timing('selenium_agent_browse_projects_list')
    def measure():
        browse_projects_page.go_to()
        browse_projects_page.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def browse_project_customers_page(webdriver, datasets):
    browse_customers_page = BrowseCustomers(webdriver, project_key=datasets['random_project_key'])

    @print_timing('selenium_agent_browse_project_customers_page')
    def measure():
        browse_customers_page.go_to()
        browse_customers_page.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_customer_request(webdriver, datasets):
    customer_request_page = ViewCustomerRequest(webdriver, request_key=datasets['request_key'])

    @print_timing('selenium_agent_view_customer_request')
    def measure():
        customer_request_page.go_to()
        customer_request_page.wait_for_page_loaded()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def add_request_comment(webdriver, datasets):
    customer_request_page = ViewCustomerRequest(webdriver, request_key=datasets['request_key'])

    @print_timing('selenium_agent_add_request_comment')
    def measure():
        customer_request_page.go_to()
        customer_request_page.wait_for_page_loaded()

        @print_timing('selenium_agent_add_request_comment:add comment')
        def sub_measure():
            customer_request_page.add_request_comment(rte_status)
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_queue_medium_project(webdriver, datasets):
    browse_queues_page = ViewQueue(webdriver, project_key=datasets['medium_project_key'],
                                   queue_id=datasets['all_open_queue_id_medium'])
    view_queue_form_diff_projects_size(browse_queues_page, project_size='large')
    PopupManager(webdriver).dismiss_default_popup()


def view_queue_small_project(webdriver, datasets):
    browse_queues_page = ViewQueue(webdriver, project_key=datasets['small_project_key'],
                                   queue_id=datasets['all_open_queue_id_small'])
    view_queue_form_diff_projects_size(browse_queues_page, project_size='small')
    PopupManager(webdriver).dismiss_default_popup()


def log_out(webdriver, datasets):
    logout_page = Logout(webdriver)
    PopupManager(webdriver).dismiss_default_popup()

    @print_timing("selenium_agent_log_out")
    def measure():
        logout_page.go_to()
        PopupManager(webdriver).dismiss_default_popup()
        logout_page.click_logout()
        logout_page.wait_for_page_loaded()
    measure()
