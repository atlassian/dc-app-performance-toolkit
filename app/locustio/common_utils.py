import csv
import functools
import inspect
import json
import logging
import random
import re
import socket
import string
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

from locust import exception, TaskSet, events

from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, JSM_SETTINGS, BAMBOO_SETTINGS, BaseAppSettings
from util.project_paths import ENV_TAURUS_ARTIFACT_DIR

TEXT_HEADERS = {
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                }
RESOURCE_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest"
}
ADMIN_HEADERS = {
    'Accept-Language': 'en-US,en;q=0.5',
    'X-AUSERNAME': 'admin',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': '*/*',
    'X-Atlassian-Token': 'no-check',
    'Content-Length': '0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'xx',
}
NO_TOKEN_HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "X-Requested-With": "XMLHttpRequest",
    "__amdModuleName": "jira/issue/utils/xsrf-token-header",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Atlassian-Token": "no-check"
}
JSON_HEADERS = {
    "Accept-Language": "en-US,en;q=0.5",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}
JSM_CUSTOMERS_HEADERS = {
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Encoding': 'gzip, deflate',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    "X-Atlassian-Token": "no-check"
}
LOGIN_BODY = {
    'os_username': '',
    'os_password': '',
    'os_destination': '',
    'os_cookie': True,
    'user_role': '',
    'atl_token': '',
    'login': 'Log in'
}
LOGIN_BODY_CONFLUENCE = {
        'os_username': '',
        'os_password': '',
        'os_cookie': True,
        'os_destination': '',
        'login': 'Log in'
    }

JIRA_TOKEN_PATTERN = r'name="atlassian-token" content="(.+?)">'
CONFLUENCE_TOKEN_PATTERN = r'"ajs-atl-token" content="(.+?)"'
CONFLUENCE_KEYBOARD_HASH_RE = 'name=\"ajs-keyboardshortcut-hash\" content=\"(.*?)\">'
CONFLUENCE_BUILD_NUMBER_RE = 'meta name=\"ajs-build-number\" content=\"(.*?)\"'

JIRA = 'jira'
JSM = 'jsm'
TYPE_AGENT = 'agent'
TYPE_CUSTOMER = 'customer'
CONFLUENCE = 'confluence'
BAMBOO = 'bamboo'

jira_action_time = 3600 / int((JIRA_SETTINGS.total_actions_per_hour) / int(JIRA_SETTINGS.concurrency))
confluence_action_time = 3600 / int((CONFLUENCE_SETTINGS.total_actions_per_hour) / int(CONFLUENCE_SETTINGS.concurrency))
jsm_agent_action_time = 3600 / int((JSM_SETTINGS.agents_total_actions_per_hr) / int(JSM_SETTINGS.agents_concurrency))
jsm_customer_action_time = 3600 / int((JSM_SETTINGS.customers_total_actions_per_hr)
                                      / int(JSM_SETTINGS.customers_concurrency))
bamboo_action_time = 3600 / int((BAMBOO_SETTINGS.total_actions_per_hour) / int(BAMBOO_SETTINGS.concurrency))


class LocustConfig:

    def __init__(self, config_yml: BaseAppSettings):
        self.env = config_yml.env_settings
        self.secure = config_yml.secure

    def percentage(self, action_name: str):
        if action_name in self.env:
            return int(self.env[action_name])
        else:
            raise Exception(f'Action percentage for {action_name} does not set in yml configuration file')


class Logger(logging.Logger):

    def __init__(self, name, level, app_type):
        super().__init__(name=name, level=level)
        self.type = app_type

    def locust_info(self, msg, *args, **kwargs):
        is_verbose = False
        if self.type.lower() == 'confluence':
            is_verbose = CONFLUENCE_SETTINGS.verbose
        elif self.type.lower() == 'jira':
            is_verbose = JIRA_SETTINGS.verbose
        elif self.type.lower() == 'jsm':
            is_verbose = JSM_SETTINGS.verbose
        elif self.type.lower() == 'bamboo':
            is_verbose = BAMBOO_SETTINGS.verbose
        if is_verbose or not self.type:
            if self.isEnabledFor(logging.INFO):
                self._log(logging.INFO, msg, args, **kwargs)


class MyBaseTaskSet(TaskSet):

    cross_action_storage = dict()  # Cross actions locust storage
    session_data_storage = dict()
    login_failed = False

    def failure_check(self, response, action_name):
        if (hasattr(response, 'error') and response.error) or not response:
            if 'login' in action_name:
                self.login_failed = True
            if response.headers.get('Content-Type') == 'application/json':
                logger.error(response.json())
            events.request.fire(request_type="Action",
                                name=f"locust_{action_name}",
                                response_time=0,
                                response_length=0,
                                context=None,
                                response=None,
                                exception=str(response.raise_for_status()))

    def get(self, *args, **kwargs):
        r = self.client.get(*args, **kwargs)
        action_name = inspect.stack()[1][3]
        self.failure_check(response=r, action_name=action_name)
        return r

    def post(self, *args, **kwargs):
        r = self.client.post(*args, **kwargs)
        action_name = inspect.stack()[1][3]
        self.failure_check(response=r, action_name=action_name)
        return r


class BaseResource:
    action_name = ''

    def __init__(self, resource_file):
        self.resources_file = resource_file
        self.resources_json = self.read_json()
        self.resources_body = self.action_resources()

    def read_json(self):
        with open(self.resources_file, encoding='UTF-8') as f:
            return json.load(f)

    def action_resources(self):
        return self.resources_json[self.action_name] if self.action_name in self.resources_json else dict()


def jira_measure(interaction=None):
    assert interaction is not None, "Interaction name is not passed to the jira_measure decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = global_measure(func, start, interaction, *args, **kwargs)
            total = (time.time() - start)
            if total < jira_action_time:
                sleep = (jira_action_time - total)
                print(f'action: {interaction}, action_execution_time: {total}, sleep {sleep}')
                time.sleep(sleep)
            return result
        return wrapper
    return deco_wrapper


def jsm_agent_measure(interaction=None):
    assert interaction is not None, "Interaction name is not passed to the jsm_agent_measure decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = global_measure(func, start, interaction, *args, **kwargs)
            total = (time.time() - start)
            if total < jsm_agent_action_time:
                sleep = (jsm_agent_action_time - total)
                print(f'action: {interaction}, action_execution_time: {total}, sleep {sleep}')
                time.sleep(sleep)
            return result
        return wrapper
    return deco_wrapper


def jsm_customer_measure(interaction=None):
    assert interaction is not None, "Interaction name is not passed to the jsm_customer_measure decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = global_measure(func, start, interaction, *args, **kwargs)
            total = (time.time() - start)
            if total < jsm_customer_action_time:
                sleep = (jsm_customer_action_time - total)
                print(f'action: {interaction}, action_execution_time: {total}, sleep {sleep}')
                time.sleep(sleep)
            return result
        return wrapper
    return deco_wrapper


def confluence_measure(interaction=None):
    assert interaction is not None, "Interaction name is not passed to the confluence_measure decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = global_measure(func, start, interaction, *args, **kwargs)
            total = (time.time() - start)
            if total < confluence_action_time:
                sleep = (confluence_action_time - total)
                logger.info(f'action: {interaction}, action_execution_time: {total}, sleep {sleep}')
                time.sleep(sleep)
            return result
        return wrapper
    return deco_wrapper


def bamboo_measure(interaction=None):
    assert interaction is not None, "Interaction name is not passed to the bamboo_measure decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = global_measure(func, start, interaction, *args, **kwargs)
            total = (time.time() - start)
            if total < bamboo_action_time:
                sleep = (bamboo_action_time - total)
                logger.info(f'action: {interaction}, action_execution_time: {total}, sleep {sleep}')
                time.sleep(sleep)
            return result
        return wrapper
    return deco_wrapper


def global_measure(func, start_time, interaction, *args, **kwargs):
    result = None
    try:
        result = func(*args, **kwargs)
    except Exception as e:
        total = int((time.time() - start_time) * 1000)
        print(e)
        events.request.fire(request_type="Action",
                            name=interaction,
                            response_time=total,
                            response_length=0,
                            response=None,
                            context=None,
                            exception=e)
        logger.error(f'{interaction} action failed. Reason: {e}')
    else:
        total = int((time.time() - start_time) * 1000)
        events.request.fire(request_type="Action",
                            name=interaction,
                            response_time=total,
                            response_length=0,
                            response=None,
                            context=None,
                            exception=None
                            )
        logger.info(f'{interaction} is finished successfully')
    return result


def read_input_file(file_path):
    with open(file_path, 'r') as fs:
        reader = csv.reader(fs)
        return list(reader)


def fetch_by_re(pattern, text, group_no=1, default_value=None):
    search = re.search(pattern, text)
    if search:
        return search.group(group_no)
    else:
        return default_value


def read_json(file_json):
    with open(file_json) as f:
        return json.load(f)


def init_logger(app_type=None):
    logfile_path = ENV_TAURUS_ARTIFACT_DIR / 'locust.log'
    root_logger = Logger(name='locust', level=logging.INFO, app_type=app_type)
    log_format = f"[%(asctime)s.%(msecs)03d] [%(levelname)s] {socket.gethostname()}/%(name)s : %(message)s"
    formatter = logging.Formatter(log_format, '%Y-%m-%d %H:%M:%S')
    file_handler = RotatingFileHandler(logfile_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    return root_logger


def timestamp_int():
    now = datetime.now()
    return int(datetime.timestamp(now))


def generate_random_string(length, only_letters=False):
    if not only_letters:
        return "".join([random.choice(string.digits + string.ascii_letters + ' ') for _ in range(length)])
    else:
        return "".join([random.choice(string.ascii_lowercase + ' ') for _ in range(length)])


def get_first_index(from_list: list, err):
    if len(from_list) > 0:
        return from_list[0]
    else:
        raise IndexError(err)


def raise_if_login_failed(locust):
    if locust.login_failed:
        raise exception.StopUser('Action login_and_view_dashboard failed')


def do_confluence_login(locust, usr, pwd):
    locust.client.cookies.clear()
    r = locust.get('/dologin.action', catch_response=True)
    content = r.content.decode('utf-8')
    is_legacy_login_form = 'loginform' in content

    if is_legacy_login_form:

        login_body = LOGIN_BODY_CONFLUENCE
        login_body['os_username'] = usr
        login_body['os_password'] = pwd

        locust.post('/dologin.action',
                    login_body,
                    TEXT_HEADERS,
                    catch_response=True)
    else:

        login_body = {'username': usr,
                      'password': pwd,
                      'rememberMe': 'True',
                      'targetUrl': ''
                      }

        headers = {
            "Content-Type": "application/json"
        }

        # 15 /rest/tsv/1.0/authenticate
        locust.post('/rest/tsv/1.0/authenticate',
                    json=login_body,
                    headers=headers,
                    catch_response=True)
    r = locust.get(url='/', catch_response=True)
    content = r.content.decode('utf-8')

    if 'Log Out' not in content:
        print(f'Login with {usr}, {pwd} failed: {content}')
    assert 'Log Out' in content, 'User authentication failed.'
    print(f'User {usr} is successfully logged in back')
    keyboard_hash = fetch_by_re(CONFLUENCE_KEYBOARD_HASH_RE, content)
    build_number = fetch_by_re(CONFLUENCE_BUILD_NUMBER_RE, content)
    token = fetch_by_re(locust.session_data_storage['token_pattern'], content)

    # 20 index.action
    locust.get('/index.action', catch_response=True)

    locust.session_data_storage['build_number'] = build_number
    locust.session_data_storage['keyboard_hash'] = keyboard_hash
    locust.session_data_storage['username'] = usr
    locust.session_data_storage['password'] = pwd
    locust.session_data_storage['token'] = token


def do_login_jira(locust, usr, pwd):
    locust.client.cookies.clear()
    body = LOGIN_BODY
    body['os_username'] = usr
    body['os_password'] = pwd

    legacy_form = False

    # Check if 2sv login form
    r = locust.get('/login.jsp', catch_response=True)
    content = r.content.decode('utf-8')
    if 'login-form-remember-me' in content:
        legacy_form = True

    # 100 /login.jsp
    if legacy_form:
        locust.post('/login.jsp', body,
                    TEXT_HEADERS,
                    catch_response=True)
    else:
        login_body = {'username': usr,
                      'password': pwd,
                      'rememberMe': 'True',
                      'targetUrl': ''
                      }

        headers = {
            "Content-Type": "application/json"
        }

        # 15 /rest/tsv/1.0/authenticate
        locust.post('/rest/tsv/1.0/authenticate',
                    json=login_body,
                    headers=headers,
                    catch_response=True)

        r = locust.get('/', catch_response=True)
        if not r.content:
            raise Exception('Please check server hostname in jira.yml file')
        if locust.session_data_storage['token_pattern']:
            content = r.content.decode('utf-8')
            token = fetch_by_re(locust.session_data_storage['token_pattern'], content)
            locust.session_data_storage["token"] = token


def run_as_specific_user(username=None, password=None):
    if not (username and password):
        raise SystemExit(f'The credentials are not valid: {{username: {username}, password: {password}}}.')

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            locust = None
            for obj in list(locals()['kwargs'].values()) + list(locals()['args']):
                if isinstance(obj, MyBaseTaskSet):
                    locust = obj
                    break

            if locust:
                session_user_name = locust.session_data_storage["username"]
                session_user_password = locust.session_data_storage["password"]
                app = locust.session_data_storage['app']
                locust.session_data_storage['token_pattern'] = None
                app_type = locust.session_data_storage.get('app_type', None)
                token_pattern = None

                # Jira or JSM Agent - redefine token value
                if app == JIRA or (app == JSM and app_type == TYPE_AGENT):
                    locust.session_data_storage['token_pattern'] = JIRA_TOKEN_PATTERN
                # Confluence - redefine token value
                elif app == CONFLUENCE:
                    locust.session_data_storage['token_pattern'] = CONFLUENCE_TOKEN_PATTERN

                # send requests by the specific user
                if app == JIRA or (app == JSM and app_type == TYPE_AGENT):
                    do_login_jira(locust, username, password)
                    func(*args, **kwargs)
                    do_login_jira(locust, session_user_name, session_user_password)

                if app == CONFLUENCE:
                    do_confluence_login(locust, username, password)
                    func(*args, **kwargs)
                    do_confluence_login(locust, session_user_name, session_user_password)

                if app not in [CONFLUENCE, JIRA, JSM]:
                    raise SystemExit(f"Unsupported app type: {app}")

            else:
                raise SystemExit(f"There is no 'locust' object in the '{func.__name__}' function.")
        return wrapper
    return deco_wrapper


logger = init_logger()
