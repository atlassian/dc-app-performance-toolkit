from selenium_ui.conftest import print_timing
from selenium_ui.jsm.pages.customer_pages import Login, TopPanel, CustomerPortals, CustomerPortal, CustomerRequest, \
    Requests, ViewRequestWithInsight
import random
from packaging import version


REQUESTS = "requests"
CUSTOMERS = "customers"
SERVICE_DESKS_LARGE = "service_desks_large"
SERVICE_DESKS_SMALL = "service_desks_small"
CUSTOM_ISSUES = "custom_issues"


def __get_random_customer_request(customer):
    customer_requests = customer[2:]
    customer_requests_chunks = [customer_requests[x:x + 3]
                                for x in range(0, len(customer_requests), 3)]
    customer_request = random.choice(customer_requests_chunks)
    service_desk_id = customer_request[0]
    request_id = customer_request[1]
    request_key = customer_request[2]
    return service_desk_id, request_id, request_key


def setup_run_data(datasets):
    customer = random.choice(datasets[CUSTOMERS])
    request = random.choice(datasets[REQUESTS])
    datasets['current_session'] = {}

    # Define users dataset
    datasets['current_session']['customer_username'] = customer[0]
    datasets['current_session']['customer_password'] = customer[1]
    customer_request = __get_random_customer_request(customer)
    datasets['current_session']['customer_service_desk_id'] = customer_request[0]
    datasets['current_session']['customer_request_id'] = customer_request[1]
    datasets['current_session']['customer_request_key'] = customer_request[2]

    # Define request dataset
    datasets['current_session']['request_id'] = request[0]
    datasets['current_session']['request_key'] = request[1]
    datasets['current_session']['service_desk_id'] = request[2]
    datasets['current_session']['project_id'] = request[3]
    datasets['current_session']['project_key'] = request[4]

    if CUSTOM_ISSUES in datasets:
        if len(datasets[CUSTOM_ISSUES]) > 0:
            custom_issue = random.choice(datasets[CUSTOM_ISSUES])
            datasets['custom_issue_key'] = custom_issue[0]
            datasets['custom_issue_id'] = custom_issue[1]
            datasets['custom_service_desk_id'] = custom_issue[3]


def generate_debug_session_info(webdriver, datasets):
    debug_data = datasets['current_session']
    debug_data['current_url'] = webdriver.current_url
    return debug_data


def login(webdriver, datasets):
    setup_run_data(datasets)

    @print_timing("selenium_customer_login")
    def measure():
        login_page = Login(webdriver)
        customer_portals = CustomerPortals(webdriver)
        webdriver.base_url = login_page.base_url
        webdriver.debug_info = generate_debug_session_info(webdriver, datasets)

        @print_timing("selenium_customer_login:open_login_page")
        def sub_measure():
            login_page.go_to()
            webdriver.app_version = login_page.get_app_version()
            if login_page.is_logged_in():
                login_page.delete_all_cookies()
                login_page.go_to()
            login_page.wait_for_page_loaded()
        sub_measure()

        @print_timing("selenium_customer_login:login_and_view_portal")
        def sub_measure():
            login_page.set_credentials(
                username=datasets['current_session']['customer_username'],
                password=datasets['current_session']['customer_password'])
            customer_portals.wait_for_page_loaded()
        sub_measure()

        current_session_response = login_page.rest_api_get(
            url=f'{webdriver.base_url}/rest/auth/latest/session')
        if 'name' in current_session_response:
            actual_username = current_session_response['name']
            assert actual_username == datasets['current_session']['customer_username']
    measure()


def create_request(webdriver, datasets):
    customer_portals = CustomerPortals(webdriver)
    customer_portal = CustomerPortal(
        webdriver, portal_id=datasets['current_session']['customer_service_desk_id'])

    @print_timing("selenium_customer_create_request")
    def measure():

        @print_timing("selenium_customer_create_request:browse_all_portals")
        def sub_measure():
            customer_portals.browse_projects()
        sub_measure()

        @print_timing("selenium_customer_create_request:view_portal")
        def sub_measure():
            customer_portal.go_to()
            customer_portal.wait_for_page_loaded()
        sub_measure()

        @print_timing("selenium_customer_create_request:choose_request_type")
        def sub_measure():
            customer_portal.chose_random_request_type()
        sub_measure()

        @print_timing("selenium_customer_create_request:create_and_submit_request")
        def sub_measure():
            customer_portal.create_and_submit_request()
        sub_measure()
    measure()


def view_request(webdriver, datasets):
    customer_request = CustomerRequest(
        webdriver,
        portal_id=datasets['current_session']['customer_service_desk_id'],
        request_key=datasets['current_session']['customer_request_key'])

    @print_timing("selenium_customer_view_request")
    def measure():
        customer_request.go_to()
        customer_request.wait_for_page_loaded()
    measure()


def view_requests(webdriver, datasets):
    my_requests = Requests(webdriver, all_requests=False)

    @print_timing("selenium_customer_view_requests")
    def measure():
        my_requests.go_to()
        my_requests.wait_for_page_loaded()
    measure()


def view_all_requests(webdriver, datasets):
    my_requests = Requests(webdriver, all_requests=True)

    @print_timing("selenium_customer_view_all_requests")
    def measure():
        my_requests.go_to()
        my_requests.wait_for_page_loaded()
    measure()


def add_comment(webdriver, datasets):
    customer_request = CustomerRequest(
        webdriver,
        portal_id=datasets['current_session']['customer_service_desk_id'],
        request_key=datasets['current_session']['customer_request_key'])

    @print_timing("selenium_customer_add_comment")
    def measure():
        customer_request.go_to()
        customer_request.wait_for_page_loaded()
        customer_request.comment_request()
    measure()


def share_request_with_customer(webdriver, datasets):
    customer_request = CustomerRequest(
        webdriver,
        portal_id=datasets['current_session']['customer_service_desk_id'],
        request_key=datasets['current_session']['customer_request_key'])
    customer_request.go_to()
    customer_request.wait_for_page_loaded()

    @print_timing("selenium_customer_share_request_with_customer")
    def measure():

        @print_timing("selenium_customer_share_request_with_customer:search_for_customer_to_share_with")
        def sub_measure():
            if webdriver.app_version >= version.parse('5.12'):
                customer_request.search_for_customer_to_share_with_react_ui(
                    customer_name='performance_customer')
            else:
                customer_request.search_for_customer_to_share_with(
                    customer_name='performance_customer')
        sub_measure()

        @print_timing("selenium_customer_share_request:share_request_with_customer")
        def sub_measure():
            if webdriver.app_version >= version.parse('5.12'):
                customer_request.share_request_react()
            else:
                customer_request.share_request()
        sub_measure()
    measure()


def view_request_with_insight(webdriver, datasets):
    view_request_with_insight_field = ViewRequestWithInsight(
        webdriver, portal_id=datasets['current_session']['customer_service_desk_id'])

    @print_timing("selenium_customer_insight_view_request_with_insight_field")
    def measure():
        view_request_with_insight_field.go_to()
        view_request_with_insight_field.choose_request_type()
        view_request_with_insight_field.check_insight_field()

    measure()


def log_out(webdriver, datasets):
    top_panel = TopPanel(webdriver)

    @print_timing("selenium_customer_log_out")
    def measure():
        top_panel.open_profile_menu()
        top_panel.logout()
    measure()
