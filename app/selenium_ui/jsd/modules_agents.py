from selenium_ui.conftest import print_timing
from selenium_ui.jsd.pages.agent_pages import Login, PopupManager, Logout, BrowseProjects, BrowseCustomers, \
    ViewCustomerRequest, ViewReports
import random

REQUESTS = "requests"
AGENTS = "agents"
REPORTS = 'reports'
SERVICE_DESKS_LARGE = "service_desks_large"
SERVICE_DESKS_SMALL = "service_desks_small"


def setup_run_data(datasets):
    agent = random.choice(datasets[AGENTS])
    request = random.choice(datasets[REQUESTS])
    service_desk_large = random.choice(datasets[SERVICE_DESKS_LARGE])
    service_desk_small = random.choice(datasets[SERVICE_DESKS_SMALL])

    # Define users dataset
    datasets['agent_username'] = agent[0]
    datasets['agent_password'] = agent[1]

    # Define request dataset
    datasets['request_id'] = request[0]
    datasets['request_key'] = request[1]

    datasets['large_project_id'] = service_desk_large[1]
    datasets['large_project_key'] = request[2]

    datasets['small_project_id'] = service_desk_small[1]
    datasets['small_project_key'] = service_desk_small[2]


def login(webdriver, datasets):
    setup_run_data(datasets)

    @print_timing("selenium_login")
    def measure():
        login_page = Login(webdriver)

        @print_timing("selenium_login:open_login_page")
        def sub_measure():
            login_page.go_to()
        sub_measure()

        @print_timing("selenium_login:login_and_view_dashboard")
        def sub_measure():
            login_page.set_credentials(username=datasets['agent_username'], password=datasets['agent_password'])
            if login_page.is_first_login():
                login_page.first_login_setup()
            login_page.wait_for_page_loaded()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def log_out(webdriver, datasets):
    logout_page = Logout(webdriver)

    @print_timing("selenium_log_out")
    def measure():
        logout_page.go_to()
        logout_page.click_logout()
        logout_page.wait_for_page_loaded()
    measure()


def browse_projects_list(webdriver, datasets):
    browse_projects_page = BrowseProjects(webdriver)

    @print_timing('selenium_browse_projects_list')
    def measure():
        browse_projects_page.go_to()
        browse_projects_page.wait_for_page_loaded()
    measure()


def browse_project_customers_page(webdriver, datasets):
    browse_customers_page = BrowseCustomers(webdriver, project_key=datasets['project_key'])

    @print_timing('selenium_browse_project_customers_page')
    def measure():
        browse_customers_page.go_to()
        browse_customers_page.wait_for_page_loaded()


def view_customer_request(webdriver, datasets):
    customer_request_page = ViewCustomerRequest(webdriver, request_key=datasets['request_key'])

    @print_timing('selenium_view_customer_request')
    def measure():
        customer_request_page.go_to()
        customer_request_page.wait_for_page_loaded()
    measure()


def view_reports(webdriver, datasets):
    browse_reports_page = ViewReports(webdriver, project_key=datasets['project_key'])

    @print_timing('selenium_view_reports')
    def measure():
        browse_reports_page.go_to()
        browse_reports_page.wait_for_page_loaded()

        @print_timing('selenium_view_reports:view_time_to_resolution_report')
        def sub_measure():
            browse_reports_page.view_time_to_resolution_report()
        sub_measure()

        @print_timing('selenium_view_reports:view_workload_report')
        def sub_measure():
            browse_reports_page.view_workload_report()
        sub_measure()

        @print_timing('selenium_view_reports:view_created_vs_resolved')
        def sub_measure():
            browse_reports_page.view_created_vs_resolved()
        sub_measure()
    measure()
