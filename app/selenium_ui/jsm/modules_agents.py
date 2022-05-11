import random

from selenium_ui.conftest import print_timing
from selenium_ui.jsm.pages.agent_pages import Login, PopupManager, Logout, BrowseProjects, BrowseCustomers, \
    ViewCustomerRequest, ViewQueue, Report, InsightLogin, InsightNewSchema, InsightNewObject, InsightDeleteSchema, \
    InsightViewQueue, ViewIssueWithObject, InsightSearchByIql
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
CUSTOM_ISSUES = "custom_issues"
INSIGHT_ISSUES = "insight_issues"
INSIGHT_SCHEMAS = "insight_schemas"


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
        datasets['m_report_created_vs_resolved_id'] = service_desk_medium[5]

    if datasets[SERVICE_DESKS_SMALL]:
        service_desk_small = random.choice(datasets[SERVICE_DESKS_SMALL])
        datasets['small_project_id'] = service_desk_small[1]
        datasets['small_project_key'] = service_desk_small[2]
        datasets['all_open_queue_id_small'] = service_desk_small[4]
        # Small projects reports
        datasets['s_report_created_vs_resolved_id'] = service_desk_small[5]

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

    if CUSTOM_ISSUES in datasets:
        if len(datasets[CUSTOM_ISSUES]) > 0:
            custom_issue = random.choice(datasets[CUSTOM_ISSUES])
            datasets['custom_issue_key'] = custom_issue[0]
            datasets['custom_issue_id'] = custom_issue[1]

    if JSM_SETTINGS.insight:
        schema_id = random.choice(datasets[INSIGHT_SCHEMAS])
        datasets['schema_id'] = schema_id[0]
        insight_issues = random.choice(datasets[INSIGHT_ISSUES])
        datasets['issue_key'] = insight_issues[0]


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
            if login_page.is_first_login_second_page():
                login_page.first_login_second_page_setup()
            login_page.wait_for_page_loaded()
            webdriver.node_id = login_page.get_node_id()
            print(f"node_id:{webdriver.node_id}")

        sub_measure()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_report_workload_medium(webdriver, datasets):
    workload_report = Report.view_workload_report(webdriver, project_key=datasets['medium_project_key'])

    @print_timing('selenium_agent_view_report_workload_medium')
    def measure():
        workload_report.go_to()
        workload_report.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_report_created_vs_resolved_medium(webdriver, datasets):
    created_vs_resolved = Report.view_created_vs_resolved_report(
        webdriver,
        project_key=datasets['medium_project_key'],
        created_vs_resolved_report_id=datasets['m_report_created_vs_resolved_id']
    )

    @print_timing('selenium_agent_view_report_created_vs_resolved_medium')
    def measure():
        created_vs_resolved.go_to()
        created_vs_resolved.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_report_workload_small(webdriver, datasets):
    workload_report = Report.view_workload_report(webdriver, project_key=datasets['small_project_key'])

    @print_timing('selenium_agent_view_report_workload_small')
    def measure():
        workload_report.go_to()
        workload_report.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_report_created_vs_resolved_small(webdriver, datasets):
    created_vs_resolved = Report.view_created_vs_resolved_report(
        webdriver, project_key=datasets['small_project_key'],
        created_vs_resolved_report_id=datasets['s_report_created_vs_resolved_id']
    )

    @print_timing('selenium_agent_view_report_created_vs_resolved_small')
    def measure():
        created_vs_resolved.go_to()
        created_vs_resolved.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_queues_form_diff_projects_size(browse_queue_page, project_size):
    @print_timing(f'selenium_agent_view_queues_{project_size}_project')
    def measure():
        @print_timing(f'selenium_agent_view_queues_{project_size}_project_:all_open_queue')
        def sub_measure():
            browse_queue_page.go_to()
            browse_queue_page.wait_for_page_loaded()

        sub_measure()

        @print_timing(f'selenium_agent_view_queues_{project_size}_project:random_choice_queue')
        def sub_measure():
            browse_queue_page.get_random_queue()

        sub_measure()

    measure()


def agent_browse_projects(webdriver, datasets):
    browse_projects_page = BrowseProjects(webdriver)

    @print_timing('selenium_agent_browse_projects')
    def measure():
        browse_projects_page.go_to()
        browse_projects_page.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_customers(webdriver, datasets):
    browse_customers_page = BrowseCustomers(webdriver, project_key=datasets['random_project_key'])

    @print_timing('selenium_agent_view_customers')
    def measure():
        browse_customers_page.go_to()
        browse_customers_page.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_request(webdriver, datasets):
    customer_request_page = ViewCustomerRequest(webdriver, request_key=datasets['request_key'])

    @print_timing('selenium_agent_view_request')
    def measure():
        customer_request_page.go_to()
        customer_request_page.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def add_comment(webdriver, datasets):
    customer_request_page = ViewCustomerRequest(webdriver, request_key=datasets['request_key'])

    @print_timing('selenium_agent_add_comment')
    def measure():
        customer_request_page.go_to()
        customer_request_page.wait_for_page_loaded()

        @print_timing('selenium_agent_add_comment:add comment')
        def sub_measure():
            customer_request_page.add_request_comment(rte_status)

        sub_measure()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_queues_medium(webdriver, datasets):
    browse_queues_page = ViewQueue(webdriver, project_key=datasets['medium_project_key'],
                                   queue_id=datasets['all_open_queue_id_medium'])
    view_queues_form_diff_projects_size(browse_queues_page, project_size='large')
    PopupManager(webdriver).dismiss_default_popup()


def view_queues_small(webdriver, datasets):
    browse_queues_page = ViewQueue(webdriver, project_key=datasets['small_project_key'],
                                   queue_id=datasets['all_open_queue_id_small'])
    view_queues_form_diff_projects_size(browse_queues_page, project_size='small')
    PopupManager(webdriver).dismiss_default_popup()


def insight_main_page(webdriver, datasets):
    view_insight_main_page = InsightLogin(webdriver)

    @print_timing("selenium_agent_insight_view_main_page")
    def measure():
        view_insight_main_page.go_to()
        view_insight_main_page.submit_login(username=datasets['agent_username'], password=datasets['agent_password'])

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def insight_create_new_schema(webdriver, datasets):
    insight_create_schema_page = InsightNewSchema(webdriver)

    @print_timing('selenium_agent_insight_create_new_schema')
    def measure():
        insight_create_schema_page.go_to()
        insight_create_schema_page.wait_for_page_loaded()
        PopupManager(webdriver).dismiss_default_popup()
        datasets['schema_name'] = insight_create_schema_page.create_new_schema()

    measure()


def insight_create_new_object(webdriver, datasets):
    insight_new_object_page = InsightNewObject(webdriver)

    @print_timing('selenium_agent_insight_create_new_object')
    def measure():
        insight_new_object_page.wait_for_page_loaded()
        insight_new_object_page.go_to_new_schema(datasets['schema_name'])
        insight_new_object_page.insight_create_new_objects()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def insight_delete_new_schema(webdriver, datasets):
    insight_delete_schema_page = InsightDeleteSchema(webdriver)

    @print_timing('selenium_agent_insight_delete_new_schema')
    def measure():
        insight_delete_schema_page.go_to()
        insight_delete_schema_page.wait_for_page_loaded()
        PopupManager(webdriver).dismiss_default_popup()
        insight_delete_schema_page.delete_new_schema(datasets['schema_name'])

    measure()


def insight_view_queue_insight_column(webdriver, datasets):
    insight_random_queue_page = InsightViewQueue(webdriver, project_key=datasets['random_project_key'])

    @print_timing('selenium_agent_insight_view_queue_with_insight_column')
    def measure():
        insight_random_queue_page.go_to()
        insight_random_queue_page.wait_for_page_loaded()
        insight_random_queue_page.view_random_queue_with_insight()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def insight_search_object_by_iql(webdriver, datasets):
    search_object_by_iql_page = InsightSearchByIql(webdriver, schema_id=datasets['schema_id'])

    @print_timing('selenium_agent_insight_search_object_by_iql')
    def measure():
        search_object_by_iql_page.go_to()
        search_object_by_iql_page.wait_for_page_loaded()
        PopupManager(webdriver).dismiss_default_popup()
        search_object_by_iql_page.search_object_by_iql()

    measure()


def view_issue_with_insight_objects(webdriver, datasets):
    view_issue_with_objects_page = ViewIssueWithObject(webdriver, insight_issues=datasets["issue_key"])

    @print_timing('selenium_agent_insight_view_issue_with_objects')
    def measure():
        view_issue_with_objects_page.go_to()
        view_issue_with_objects_page.wait_for_page_loaded()
        view_issue_with_objects_page.view_issue_with_insight_custom_field()

    measure()


def logout(webdriver, datasets):
    logout_page = Logout(webdriver)
    PopupManager(webdriver).dismiss_default_popup()

    @print_timing("selenium_agent_logout")
    def measure():
        logout_page.go_to()
        PopupManager(webdriver).dismiss_default_popup()
        logout_page.click_logout()
        logout_page.wait_for_page_loaded()

    measure()
