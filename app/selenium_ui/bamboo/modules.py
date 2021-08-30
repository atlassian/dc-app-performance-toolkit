import random

from selenium_ui.bamboo.pages.pages import Login, Logout
from selenium_ui.conftest import print_timing

USERS = "users"
BUILD_PLANS = "build_plans"


def setup_run_data(datasets):
    user = random.choice(datasets[USERS])
    datasets['username'] = user[0]
    datasets['password'] = user[1]


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
