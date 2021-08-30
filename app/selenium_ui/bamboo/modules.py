import random

from selenium_ui.bamboo.pages.pages import Login, Logout
from selenium_ui.conftest import print_timing

from util.api.bamboo_clients import BambooClient
from util.conf import BAMBOO_SETTINGS

client = BambooClient(BAMBOO_SETTINGS.server_url, BAMBOO_SETTINGS.admin_login, BAMBOO_SETTINGS.admin_password)

USERS = "users"
BUILD_PLANS = "build_plans"


def setup_run_data(datasets):
    user = random.choice(datasets[USERS])
    plans = random.choice(datasets[BUILD_PLANS])
    if BUILD_PLANS in datasets:
        if len(datasets[BUILD_PLANS]) > 0:
            custom_page = random.choice(datasets[BUILD_PLANS])
            datasets['build_plans'] = custom_page[0]
    datasets['username'] = user[0]
    datasets['password'] = user[1]
    datasets['build_plans'] = plans[0]


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


def log_out(webdriver, datasets):
    @print_timing("selenium_log_out")
    def measure():
        logout_page = Logout(webdriver)
        logout_page.go_to()

    measure()
