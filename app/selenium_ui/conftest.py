import atexit
import csv
import datetime
import glob
import json
import os
import random
import string
import sys
import time
from pathlib import Path

import pytest
import yaml
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from util.project_paths import JIRA_YML, JIRA_DATASET_ISSUES, JIRA_DATASET_USERS, JIRA_DATASET_JQLS, \
    JIRA_DATASET_SCRUM_BOARDS, JIRA_DATASET_KANBAN_BOARDS, JIRA_DATASET_PROJECT_KEYS

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

JTL_HEADER = "timeStamp,elapsed,label,responseCode,responseMessage,threadName,success,bytes,grpThreads,allThreads," \
             "Latency,Hostname,Connect\n"

# create selenium output files
try:
    # TODO consider using TAURUS_ARTIFACTS_DIR env variable
    latest_results_dir = max(glob.glob((str((Path("results") / "jira").absolute()) + '/20*')), key=os.path.getmtime)
except ValueError:
    # TODO we have error here if 'results' dir does not exist
    results_dir_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pytest_run_results = f'results/{results_dir_name}_local'
    os.mkdir(pytest_run_results)
    latest_results_dir = pytest_run_results  # in case you just run pytest

selenium_results_file = Path(latest_results_dir + '/selenium.jtl')
selenium_error_file = Path(latest_results_dir + '/selenium.err')
w3c_timings_file = Path(latest_results_dir + '/w3c_timings.txt')

if not selenium_results_file.exists():
    with open(selenium_results_file, "w") as file:
        file.write(JTL_HEADER)
    with open(w3c_timings_file, 'w'):
        pass


def application_url():
    with JIRA_YML.open(mode='r') as fs:
        jira_yaml = yaml.load(fs, Loader=yaml.FullLoader)
        protocol = jira_yaml['settings']['env']['application_protocol']
        hostname = jira_yaml['settings']['env']['application_hostname']
        port = str(jira_yaml['settings']['env']['application_port'])
        postfix = jira_yaml['settings']['env']['application_postfix']
        app_url = f"{protocol}://{hostname}:{port}{postfix or ''}"
        return app_url


def datetime_now(prefix):
    symbols = str(datetime.datetime.now()).replace(':', '-').replace(' ', '-')
    return prefix + "-" + "".join(symbols)


def print_timing(func):
    def wrapper(webdriver, interaction):
        start = time.time()
        error_msg = 'Success'
        full_exception = ''
        try:
            func(webdriver, interaction)
            success = True
        except Exception:
            success = False
            # https://docs.python.org/2/library/sys.html#sys.exc_info
            exc_type, full_exception = sys.exc_info()[:2]
            error_msg = exc_type.__name__
        end = time.time()
        timing = str(int((end - start) * 1000))

        with open(selenium_results_file, "a+") as file:
            timestamp = round(time.time() * 1000)
            file.write(f"{timestamp},{timing},{interaction},,{error_msg},,{success},0,0,0,0,,0\n")

        print(f"{timestamp},{timing},{interaction},{error_msg},{success}")

        w3c_timing = json.dumps(webdriver.execute_script("return window.performance.getEntries()"))
        with open(w3c_timings_file, "a+") as file:
            file.write(f"{{\"timestamp\": {timestamp}, \"timing\": {timing}, \"interation\": \"{interaction}\", "
                       f"\"error\": \"{error_msg}\", \"success\": \"{success}\", \"w3c_timing\": {w3c_timing}}}\n")

        if not success:
            raise Exception(error_msg, full_exception)

    return wrapper


@pytest.fixture(scope="module")
def webdriver():
    # TODO consider extract common logic with globals to separate function
    global driver
    if 'driver' in globals():
        driver = globals()['driver']
        return driver
    else:
        chrome_options = Options()
        if os.getenv('WEBDRIVER_VISIBLE', 'False').lower() != 'true':
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size={},{}".format(SCREEN_WIDTH, SCREEN_HEIGHT))
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-infobars")
        driver = Chrome(options=chrome_options)
        return driver


# Global instance driver quit
def driver_quit():
    driver.quit()


atexit.register(driver_quit)


def generate_random_string(length):
    return "".join([random.choice(string.digits + string.ascii_letters + ' ') for _ in range(length)])


def generate_jqls(max_length=3, count=100):
    # Generate jqls like "abc*"
    return ['text ~ "{}*" order by key'.format(
        ''.join(random.choices(string.ascii_lowercase, k=random.randrange(1, max_length + 1)))) for _ in range(count)]


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    # Making test result information available in fixtures
    # https://docs.pytest.org/en/latest/example/simple.html#making-test-result-information-available-in-fixtures
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


@pytest.fixture
def screen_shots(request, webdriver):
    yield
    # request.node is an "item" because we use the default
    # "function" scope
    if request.node.rep_call.failed:
        mode = "w" if not selenium_error_file.exists() else "a+"
        action_name = request.node.rep_call.head_line
        error_text = request.node.rep_call.longreprtext
        with open(selenium_error_file, mode) as err_file:
            err_file.write(f"Action: {action_name}, Error: {error_text}\n")
        print(f"Action: {action_name}, Error: {error_text}\n")
        os.makedirs(f"{latest_results_dir}/errors_artifacts", exist_ok=True)
        error_artifact_name = f'{latest_results_dir}/errors_artifacts/{datetime_now(action_name)}'
        webdriver.save_screenshot('{}.png'.format(error_artifact_name))
        with open(f'{error_artifact_name}.html', 'wb') as html_file:
            html_file.write(webdriver.page_source.encode('utf-8'))
        webdriver.execute_script("window.onbeforeunload = function() {};")  # to prevent alert window (force get link)
        webdriver.get(application_url())


@pytest.fixture(scope="module")
def datasets():
    # TODO consider extract common logic with globals to separate function
    global data_sets
    if 'data_sets' in globals():
        data_sets = globals()['data_sets']

        return data_sets
    else:
        data_sets = dict()
        data_sets["issues"] = __read_input_file(JIRA_DATASET_ISSUES)
        data_sets["users"] = __read_input_file(JIRA_DATASET_USERS)
        data_sets["jqls"] = __read_input_file(JIRA_DATASET_JQLS)
        data_sets["scrum_boards"] = __read_input_file(JIRA_DATASET_SCRUM_BOARDS)
        data_sets["kanban_boards"] = __read_input_file(JIRA_DATASET_KANBAN_BOARDS)
        data_sets["project_keys"] = __read_input_file(JIRA_DATASET_PROJECT_KEYS)

        return data_sets


def __read_input_file(file_path):
    with open(file_path, 'r') as fs:
        reader = csv.reader(fs)
        return list(reader)


class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """

    def __init__(self, *args):
        self.ecs = args

    def __call__(self, w_driver):
        for fn in self.ecs:
            try:
                if fn(w_driver):
                    return True
            except:
                pass
