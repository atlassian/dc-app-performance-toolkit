from selenium_ui.conftest import print_timing
from util.conf import JSD_SETTINGS
from selenium_ui.jsd.pages.customer_pages import Login, CustomerPortals, TopPanel
import random

REQUESTS = "requests"
CUSTOMERS = "customers"
SERVICE_DESKS = "service_desks"


def __get_random_customer_request(customer):
    if len(customer) > 2:  # [username, password]
        customer_requests = customer[2:]
        random_index = random.randrange(0, len(customer_requests))
        if random_index % 2 == 0:
            service_desk_id = customer_requests[random_index]
            request_key = customer_requests[random_index + 1]
        else:
            request_key = customer_requests[random_index]
            service_desk_id = customer_requests[random_index - 1]
        return service_desk_id, request_key


def setup_run_data(datasets):
    customer = random.choice(datasets[CUSTOMERS])
    request = random.choice(datasets[REQUESTS])
    service_desk = random.choice(datasets[SERVICE_DESKS])

    # Define users dataset
    datasets['customer_username'] = customer[0]
    datasets['customer_password'] = customer[1]
    customer_request = __get_random_customer_request(customer)
    if customer_request:
        datasets['customer_service_desk_id'] = customer_request[0]
        datasets['customer_request_key'] = customer_request[1]
    print('asd')

    # Define request dataset
    datasets['request_id'] = request[0]
    datasets['request_key'] = request[1]
    datasets['service_desk_id'] = request[2]
    datasets['project_id'] = request[3]
    datasets['project_key'] = request[4]


def login(webdriver, datasets):
    setup_run_data(datasets)

    @print_timing("selenium_customer_login")
    def measure():
        login_page = Login(webdriver)

        @print_timing("selenium_customer_login:open_login_page")
        def sub_measure():
            login_page.go_to()
        sub_measure()

        @print_timing("selenium_customer_login:login_and_view_dashboard")
        def sub_measure():
            login_page.set_credentials(username=datasets['customer_username'], password=datasets['customer_password'])
            login_page.wait_for_page_loaded()
        sub_measure()
    measure()


def view_customer_portals(webdriver, datasets):
    customer_portals = CustomerPortals(webdriver)

    @print_timing("selenium_customer_login:open_login_page")
    def sub_measure():
        customer_portals.go_to()
        customer_portals.wait_for_page_loaded()
    sub_measure()


def log_out(webdriver, datasets):
    top_panel = TopPanel(webdriver)

    @print_timing("selenium_customer_log_out")
    def measure():
        top_panel.open_profile_menu()
        top_panel.logout()
    measure()

