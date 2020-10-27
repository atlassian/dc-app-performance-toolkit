from selenium_ui.conftest import print_timing
from util.conf import JSD_SETTINGS
from selenium_ui.jsd.pages.agent_pages import Login, PopupManager, Logout
import random

REQUESTS = "requests"
AGENTS = "agents"
SERVICE_DESKS = "service_desks"


def setup_run_data(datasets):
    agent = random.choice(datasets[AGENTS])
    request = random.choice(datasets[REQUESTS])
    service_desk = random.choice(datasets[SERVICE_DESKS])

    # Define users dataset
    datasets['agent_username'] = agent[0]
    datasets['agent_password'] = agent[1]

    # Define request dataset
    datasets['request_id'] = request[0]
    datasets['request_key'] = request[1]
    datasets['service_desk_id'] = request[2]
    datasets['project_id'] = request[3]
    datasets['project_key'] = request[4]


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