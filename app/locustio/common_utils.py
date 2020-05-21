from locust import events
import time
import csv
import re
import logging
import random
import string
import json
import os
import inspect
import socket
from logging.handlers import RotatingFileHandler
from util.project_paths import JIRA_DATASET_ISSUES, JIRA_DATASET_JQLS, JIRA_DATASET_KANBAN_BOARDS, \
    JIRA_DATASET_PROJECT_KEYS, JIRA_DATASET_SCRUM_BOARDS, JIRA_DATASET_USERS
from datetime import datetime
from util.conf import JIRA_SETTINGS


jira_total_requests_per_hr = JIRA_SETTINGS.scenarios['locust']['properties']['total_actions_per_hr']
jira_action_time = 3600 / (jira_total_requests_per_hr / JIRA_SETTINGS.concurrency)


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


def jira_datasets():
    data_sets = dict()
    data_sets["issues"] = read_input_file(JIRA_DATASET_ISSUES)
    data_sets["users"] = read_input_file(JIRA_DATASET_USERS)
    data_sets["jqls"] = read_input_file(JIRA_DATASET_JQLS)
    data_sets["scrum_boards"] = read_input_file(JIRA_DATASET_SCRUM_BOARDS)
    data_sets["kanban_boards"] = read_input_file(JIRA_DATASET_KANBAN_BOARDS)
    data_sets["project_keys"] = read_input_file(JIRA_DATASET_PROJECT_KEYS)
    page_size = 25
    projects_count = len(data_sets['project_keys'])
    data_sets['pages'] = projects_count // page_size if projects_count % page_size == 0 \
        else projects_count // page_size + 1
    return data_sets


def measure(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            total = int((time.time() - start) * 1000)
            events.request_failure.fire(request_type="Action",
                                        name=f"locust_{func.__name__}",
                                        response_time=total,
                                        exception=e,
                                        response_length=0)
        else:
            total = int((time.time() - start) * 1000)
            events.request_success.fire(request_type="Action",
                                        name=f"locust_{func.__name__}",
                                        response_time=total,
                                        response_length=0)
        total = (time.time() - start)
        if total < jira_action_time:
            sleep = (jira_action_time - total)
            print(f'action: {func.__name__}, action_execution_time: {total}, sleep {sleep}')
            time.sleep(sleep)
        return result
    return wrapper


def init_logger():
    taurus_result_dir = 'TAURUS_ARTIFACTS_DIR'
    if taurus_result_dir in os.environ:
        artifacts_dir = os.environ.get(taurus_result_dir)
        logfile_path = f"{artifacts_dir}/locust.log"
    else:
        logfile_path = 'locust_local.log'
    root_logger = logging.getLogger()
    log_format = f"[%(asctime)s.%(msecs)03d] [%(levelname)s] {socket.gethostname()}/%(name)s : %(message)s"
    formatter = logging.Formatter(log_format, '%Y-%m-%d %H:%M:%S')
    file_handler = RotatingFileHandler(logfile_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)


def timestamp_int():
    now = datetime.now()
    return int(datetime.timestamp(now))


def generate_random_string(length):
    return "".join([random.choice(string.digits + string.ascii_letters + ' ') for _ in range(length)])


def get_first_index(from_list: list, err):
    if len(from_list) > 0:
        return from_list[0]
    else:
        raise IndexError(err)


jira_dataset = jira_datasets()
