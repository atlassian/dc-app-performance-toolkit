import atexit
import csv
import datetime
import functools
import json
import os
import sys
import time
from datetime import timezone
import re

import filelock
import pytest
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from time import sleep

from util.conf import CONFLUENCE_SETTINGS, JIRA_SETTINGS, BITBUCKET_SETTINGS, JSM_SETTINGS, BAMBOO_SETTINGS
from util.exceptions import WebDriverExceptionPostpone
from util.project_paths import JIRA_DATASET_ISSUES, JIRA_DATASET_JQLS, JIRA_DATASET_KANBAN_BOARDS, \
    JIRA_DATASET_PROJECTS, JIRA_DATASET_SCRUM_BOARDS, JIRA_DATASET_USERS, JIRA_DATASET_CUSTOM_ISSUES, BITBUCKET_USERS, \
    BITBUCKET_PROJECTS, BITBUCKET_REPOS, BITBUCKET_PRS, CONFLUENCE_BLOGS, CONFLUENCE_PAGES, CONFLUENCE_CUSTOM_PAGES, \
    CONFLUENCE_USERS, ENV_TAURUS_ARTIFACT_DIR, JSM_DATASET_REQUESTS, JSM_DATASET_CUSTOMERS, JSM_DATASET_AGENTS, \
    JSM_DATASET_SERVICE_DESKS_L, JSM_DATASET_SERVICE_DESKS_M, JSM_DATASET_SERVICE_DESKS_S, JSM_DATASET_CUSTOM_ISSUES,\
    JSM_DATASET_INSIGHT_SCHEMAS, JSM_DATASET_INSIGHT_ISSUES, BAMBOO_USERS, BAMBOO_BUILD_PLANS

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

JTL_HEADER = "timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads," \
             "Latency,Hostname,Connect\n"
LOGIN_ACTION_NAME = 'login'


class InitGlobals:
    def __init__(self):
        self.driver = None
        self.driver_title = False
        self.login_failed = False


class Dataset:
    def __init__(self):
        self.dataset = dict()

    def jira_dataset(self):
        if not self.dataset:
            self.dataset["issues"] = self.__read_input_file(JIRA_DATASET_ISSUES)
            self.dataset["users"] = self.__read_input_file(JIRA_DATASET_USERS)
            self.dataset["jqls"] = self.__read_input_file(JIRA_DATASET_JQLS)
            self.dataset["scrum_boards"] = self.__read_input_file(JIRA_DATASET_SCRUM_BOARDS)
            self.dataset["kanban_boards"] = self.__read_input_file(JIRA_DATASET_KANBAN_BOARDS)
            self.dataset["projects"] = self.__read_input_file(JIRA_DATASET_PROJECTS)
            self.dataset["custom_issues"] = self.__read_input_file(JIRA_DATASET_CUSTOM_ISSUES)
        return self.dataset

    def jsm_dataset(self):
        if not self.dataset:
            self.dataset["requests"] = self.__read_input_file(JSM_DATASET_REQUESTS)
            self.dataset["customers"] = self.__read_input_file(JSM_DATASET_CUSTOMERS)
            self.dataset["agents"] = self.__read_input_file(JSM_DATASET_AGENTS)
            self.dataset["service_desks_large"] = self.__read_input_file(JSM_DATASET_SERVICE_DESKS_L)
            self.dataset["service_desks_small"] = self.__read_input_file(JSM_DATASET_SERVICE_DESKS_S)
            self.dataset["service_desks_medium"] = self.__read_input_file(JSM_DATASET_SERVICE_DESKS_M)
            self.dataset["custom_issues"] = self.__read_input_file(JSM_DATASET_CUSTOM_ISSUES)
            self.dataset["insight_schemas"] = self.__read_input_file(JSM_DATASET_INSIGHT_SCHEMAS)
            self.dataset["insight_issues"] = self.__read_input_file(JSM_DATASET_INSIGHT_ISSUES)
        return self.dataset

    def confluence_dataset(self):
        if not self.dataset:
            self.dataset["pages"] = self.__read_input_file(CONFLUENCE_PAGES)
            self.dataset["blogs"] = self.__read_input_file(CONFLUENCE_BLOGS)
            self.dataset["users"] = self.__read_input_file(CONFLUENCE_USERS)
            self.dataset["custom_pages"] = self.__read_input_file(CONFLUENCE_CUSTOM_PAGES)
        return self.dataset

    def bitbucket_dataset(self):
        if not self.dataset:
            self.dataset["projects"] = self.__read_input_file(BITBUCKET_PROJECTS)
            self.dataset["users"] = self.__read_input_file(BITBUCKET_USERS)
            self.dataset["repos"] = self.__read_input_file(BITBUCKET_REPOS)
            self.dataset["pull_requests"] = self.__read_input_file(BITBUCKET_PRS)
        return self.dataset

    def bamboo_dataset(self):
        if not self.dataset:
            self.dataset["users"] = self.__read_input_file(BAMBOO_USERS)
            self.dataset["build_plans"] = self.__read_input_file(BAMBOO_BUILD_PLANS)

        return self.dataset

    @staticmethod
    def __read_input_file(file_path):
        with open(file_path, 'r') as fs:
            reader = csv.reader(fs)
            return list(reader)


globals = InitGlobals()

selenium_results_file = ENV_TAURUS_ARTIFACT_DIR / 'selenium.jtl'
selenium_error_file = ENV_TAURUS_ARTIFACT_DIR / 'selenium.err'

if not selenium_results_file.exists():
    with open(selenium_results_file, "w") as file:
        file.write(JTL_HEADER)


def datetime_now(prefix):
    symbols = str(datetime.datetime.now()).replace(':', '-').replace(' ', '-')
    return prefix + "-" + "".join(symbols)


def is_docker():
    path = '/proc/self/cgroup'
    return (
            os.path.exists('/.dockerenv') or
            os.path.isfile(path) and any('docker' in line for line in open(path))
    )


def print_timing(interaction=None, explicit_timing=None):
    assert interaction is not None, "Interaction name is not passed to print_timing decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper():
            if LOGIN_ACTION_NAME in interaction:
                globals.login_failed = False
            if globals.login_failed:
                pytest.skip(f"login is failed")
            start = time.time()
            error_msg = 'Success'
            full_exception = ''
            try:
                func()
                success = True
            except Exception:
                success = False
                # https://docs.python.org/2/library/sys.html#sys.exc_info
                exc_type, full_exception = sys.exc_info()[:2]
                error_msg = f"Failed measure: {interaction} - {exc_type.__name__}"
            end = time.time()
            timing = str(int((end - start) * 1000))

            lockfile = f'{selenium_results_file}.lock'

            with filelock.SoftFileLock(lockfile):
                with open(selenium_results_file, "a+") as jtl_file:
                    timestamp = round(time.time() * 1000)
                    if explicit_timing:
                        jtl_file.write(f"{timestamp},{explicit_timing*1000},{interaction},,{error_msg},"
                                       f",{success},0,0,0,0,,0\n")
                    else:
                        jtl_file.write(f"{timestamp},{timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")

            print(f"{timestamp},{timing},{interaction},{error_msg},{success}")

            if not success:
                if LOGIN_ACTION_NAME in interaction:
                    globals.login_failed = True
                raise Exception(error_msg, full_exception)

        return wrapper

    return deco_wrapper


def webdriver(app_settings):
    def driver_init():
        chrome_options = Options()
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        if app_settings.webdriver_visible and is_docker():
            raise SystemExit("ERROR: WEBDRIVER_VISIBLE is True in .yml, but Docker container does not have a display.")
        if not app_settings.webdriver_visible:
            chrome_options.add_argument("--headless")
        if not app_settings.secure:
            chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument("--window-size={},{}".format(SCREEN_WIDTH, SCREEN_HEIGHT))
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument('lang=en')
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        driver = Chrome(options=chrome_options, desired_capabilities=capabilities)
        driver.app_settings = app_settings
        return driver

    # First time driver init
    try:
        if not globals.driver:
            driver = driver_init()
            print('first driver inits')

            def driver_quit():
                driver.quit()

            globals.driver = driver
            atexit.register(driver_quit)
            return driver
        else:
            try:
                # check if driver is not broken
                globals.driver_title = globals.driver.title
                print('get driver from global')
                globals.driver.delete_all_cookies()
                print('clear browser cookies')
                return globals.driver
            except WebDriverException:
                # re-init driver if it broken
                globals.driver = driver_init()
                print('reinit driver')
                return globals.driver

    except Exception as err:
        return WebDriverExceptionPostpone(str(err))


def get_performance_logs(webdriver):
    logs = webdriver.get_log("performance")
    needed_logs = []
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if log["method"] == "Network.requestWillBeSent" or \
           log["method"] == "Network.responseReceived" or \
           log["method"] == "Network.requestServedFromCache" or \
           log["method"] == "Network.loadingFinished":
            needed_logs.append(log)

    sorted_requests = {}
    for request in needed_logs:
        request_id = request['params']['requestId']
        if request_id not in sorted_requests:
            sorted_requests[request_id] = []
        if request_id in sorted_requests:
            sorted_requests[request_id].append(request)

    return sorted_requests


def get_requests_by_url(requests, url_path):
    filtered_requests = {}
    for request_id, requests in requests.items():
        for request in requests:
            if request["method"] == 'Network.requestWillBeSent':
                if url_path in request["params"]["request"]["url"]:
                    filtered_requests[request_id] = requests
    return filtered_requests


def get_wait_browser_metrics(webdriver, expected_metrics):
    attempts = 15
    sleep_time = 0.5
    data = {}

    for i in range(attempts):
        requests = get_performance_logs(webdriver)
        requests_bulk = get_requests_by_url(requests, 'bulk')
        data.update(requests_bulk)

        if all([metric in str(data) for metric in expected_metrics]):
            return data

        print(f'Waiting for browser metrics, attempt {i}, sleep {sleep_time}')
        time.sleep(sleep_time)

    return {}


def measure_dom_requests(webdriver, interaction, description=''):
    if CONFLUENCE_SETTINGS.extended_metrics:
        if description:
            interaction = f"{interaction}-{description}"
    timing = webdriver.execute_script(
        "return window.performance.timing.loadEventEnd - window.performance.timing.navigationStart;")
    lockfile = f'{selenium_results_file}.lock'
    error_msg = ''
    success = True
    with filelock.SoftFileLock(lockfile):
        with open(selenium_results_file, "a+") as jtl_file:
            timestamp = round(time.time() * 1000)
            jtl_file.write(f"{timestamp},{timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")


def measure_browser_navi_metrics(webdriver, dataset, expected_metrics):
    requests = get_wait_browser_metrics(webdriver, expected_metrics)
    metrics = []
    for request_id, request in requests.items():
        if 'browser.metrics.navigation' in str(request):
            post_data_str = request[0]['params']['request']['postData']
            post_data = eval(post_data_str.replace('true', 'True').replace('false', 'False'))
            for data in post_data:
                if data['name'] == 'browser.metrics.navigation':
                    key = data['properties']['key']
                    ready_for_user = data['properties']['readyForUser']
                    mark = ''
                    if 'blogpost.view' in key:
                        blogpost_template_id = dataset['view_blog'][2]
                        mark = f'-view_blog-{blogpost_template_id}'
                        print(f'BLOGPOST_FOUND {mark}')
                    if 'page.view' in key:
                        if 'pageID' in post_data_str:
                            page_id = re.search('"pageID":"(.+?)"', post_data_str).group(1)

                            for name, value in dataset.items():
                                if value:
                                    if page_id == value[0]:  # [page_id, project_id, template_id]
                                        mark = f'-{name}-{value[2]}'
                                        break
                                    else:
                                        mark = f'-create_page'

                    ready_for_user_dict = {'key': f'{key}{mark}', 'ready_for_user': ready_for_user}
                    metrics.append(ready_for_user_dict)

    lockfile = f'{selenium_results_file}.lock'
    error_msg = 'Success'
    success = True
    if metrics:
        with filelock.SoftFileLock(lockfile):
            with open(selenium_results_file, "a+") as jtl_file:
                for metric in metrics:
                    interaction = metric['key']
                    ready_for_user_timing = metric['ready_for_user']
                    timestamp = round(time.time() * 1000)
                    jtl_file.write(
                        f"{timestamp},{ready_for_user_timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")
                    print(f"{timestamp},{ready_for_user_timing},{interaction},{error_msg},{success}")


@pytest.fixture(scope="module")
def jira_webdriver():
    return webdriver(app_settings=JIRA_SETTINGS)


@pytest.fixture(scope="module")
def jsm_webdriver():
    return webdriver(app_settings=JSM_SETTINGS)


@pytest.fixture(scope="module")
def confluence_webdriver():
    return webdriver(app_settings=CONFLUENCE_SETTINGS)


@pytest.fixture(scope="module")
def bitbucket_webdriver():
    return webdriver(app_settings=BITBUCKET_SETTINGS)


@pytest.fixture(scope="module")
def bamboo_webdriver():
    return webdriver(app_settings=BAMBOO_SETTINGS)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    # Making test result information available in fixtures
    # https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def jira_screen_shots(request, jira_webdriver):
    yield
    get_screen_shots(request, jira_webdriver)


@pytest.fixture
def jsm_screen_shots(request, jsm_webdriver):
    yield
    get_screen_shots(request, jsm_webdriver)


@pytest.fixture
def confluence_screen_shots(request, confluence_webdriver):
    yield
    get_screen_shots(request, confluence_webdriver)


@pytest.fixture
def bitbucket_screen_shots(request, bitbucket_webdriver):
    yield
    get_screen_shots(request, bitbucket_webdriver)


@pytest.fixture
def bamboo_screen_shots(request, bamboo_webdriver):
    yield
    get_screen_shots(request, bamboo_webdriver)


def get_screen_shots(request, webdriver):
    # request.node is an "item" because we use the default
    # "function" scope
    if request.node.rep_call.failed:
        mode = "w" if not selenium_error_file.exists() else "a+"
        action_name = request.node.rep_call.head_line
        error_text = request.node.rep_call.longreprtext
        with open(selenium_error_file, mode) as err_file:
            timestamp = round(time.time() * 1000)
            dt = datetime.datetime.now()
            utc_time = dt.replace(tzinfo=timezone.utc)
            str_time = utc_time.strftime("%m-%d-%Y, %H:%M:%S")
            str_time_stamp = f'{str_time}, {timestamp}'
            err_file.write(f"{str_time_stamp}, Action: {action_name}, Error: {error_text}\n")
        print(f"Action: {action_name}, Error: {error_text}\n")
        errors_artifacts = ENV_TAURUS_ARTIFACT_DIR / 'errors_artifacts'
        errors_artifacts.mkdir(parents=True, exist_ok=True)
        error_artifact_name = errors_artifacts / datetime_now(action_name)
        webdriver.save_screenshot('{}.png'.format(error_artifact_name))
        with open(f'{error_artifact_name}.html', 'wb') as html_file:
            html_file.write(webdriver.page_source.encode('utf-8'))
        webdriver.execute_script("window.onbeforeunload = function() {};")  # to prevent alert window (force get link)
        webdriver.get(webdriver.app_settings.server_url)


application_dataset = Dataset()


@pytest.fixture(scope="module")
def jira_datasets():
    return application_dataset.jira_dataset()


@pytest.fixture(scope="module")
def jsm_datasets():
    return application_dataset.jsm_dataset()


@pytest.fixture(scope="module")
def confluence_datasets():
    return application_dataset.confluence_dataset()


@pytest.fixture(scope="module")
def bitbucket_datasets():
    return application_dataset.bitbucket_dataset()


@pytest.fixture(scope="module")
def bamboo_datasets():
    return application_dataset.bamboo_dataset()


def retry(tries=4, delay=0.5, backoff=2, retry_exception=None):
    """
    Retry "tries" times, with initial "delay", increasing delay "delay*backoff" each time.
    """
    assert tries > 0, "tries must be 1 or greater"
    if not retry_exception:
        retry_exception = Exception

    def deco_retry(f):
        @functools.wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay

            while mtries > 0:
                sleep(mdelay)
                mdelay *= backoff
                try:
                    return f(*args, **kwargs)
                except retry_exception as e:
                    print(repr(e))
                print(f'Retrying: {mtries}')
                mtries -= 1
                if mtries == 0:
                    return f(*args, **kwargs)  # extra try, to avoid except-raise syntax

        return f_retry

    return deco_retry
