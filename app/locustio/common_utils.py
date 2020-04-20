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


def read_input_file(file_path):
    with open(file_path, 'r') as fs:
        reader = csv.reader(fs)
        return list(reader)


def fetch_by_re(pattern, text, group_no=1, default_value=""):
    search = re.search(pattern, text)
    if search:
        return search.group(group_no)
    else:
        return default_value


def read_json(file_json):
    with open(file_json) as f:
        return json.load(f)


def datasets():
    data_sets = dict()
    data_sets["issues"] = read_input_file(JIRA_DATASET_ISSUES)
    data_sets["users"] = read_input_file(JIRA_DATASET_USERS)
    data_sets["jqls"] = read_input_file(JIRA_DATASET_JQLS)
    data_sets["scrum_boards"] = read_input_file(JIRA_DATASET_SCRUM_BOARDS)
    data_sets["kanban_boards"] = read_input_file(JIRA_DATASET_KANBAN_BOARDS)
    data_sets["project_keys"] = read_input_file(JIRA_DATASET_PROJECT_KEYS)

    return data_sets


def measure(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            total = int((time.time() - start) * 1000)
            events.request_failure.fire(request_type="Locust",
                                        name=func.__name__,
                                        response_time=total,
                                        exception=e,
                                        response_length=0)
        else:
            total = int((time.time() - start) * 1000)
            events.request_success.fire(request_type="Locust",
                                        name=func.__name__,
                                        response_time=total,
                                        response_length=0)
        return result
    return wrapper


def init_logger():
    taurus_result_dir = 'TAURUS_ARTIFACTS_DIR'
    if taurus_result_dir in os.environ:
        artifacts_dir = os.environ.get(taurus_result_dir)
        logfile_path = f"{artifacts_dir}/locust.log"
    else:
        logfile_path = 'locust.log'
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


def prepare_issue_body(issue_body_dict: dict, user):
    description = f"Locust description {generate_random_string(20)}"
    summary = f"Locust summary {generate_random_string(10)}"
    environment = f'Locust environment {generate_random_string(10)}'
    duedate = ""
    reporter = user
    timetracking_originalestimate = ""
    timetracking_remainingestimate = ""
    is_create_issue = "true"
    has_work_started = ""
    project_id = issue_body_dict['project_id']
    atl_token = issue_body_dict['atl_token']
    form_token = issue_body_dict['form_token']
    issue_type = issue_body_dict['issue_type']
    resolution_done = issue_body_dict['resolution_done']
    fields_to_retain = issue_body_dict['fields_to_retain']
    custom_fields_to_retain = issue_body_dict['custom_fields_to_retain']

    request_body = f"pid={project_id}&issuetype={issue_type}&atl_token={atl_token}&formToken={form_token}" \
                   f"&summary={summary}&duedate={duedate}&reporter={reporter}&environment={environment}" \
                   f"&description={description}&timetracking_originalestimate={timetracking_originalestimate}" \
                   f"&timetracking_remainingestimate={timetracking_remainingestimate}" \
                   f"&is_create_issue={is_create_issue}&hasWorkStarted={has_work_started}&resolution={resolution_done}"
    fields_to_retain_body = ''
    custom_fields_to_retain_body = ''
    for field in fields_to_retain:
        fields_to_retain_body = fields_to_retain_body + 'fieldsToRetain=' + field[0] + '&'
    for custom_field in custom_fields_to_retain:
        custom_fields_to_retain_body = custom_fields_to_retain_body + 'fieldsToRetain=customfield_' \
                                       + custom_field[0] + '&'
    custom_fields_to_retain_body = custom_fields_to_retain_body[:-1]  # remove last &
    request_body = request_body + f"&{fields_to_retain_body}{custom_fields_to_retain_body}"
    return request_body


def prepare_jql_body(issue_ids):
    request_body = "layoutKey=split-view"
    issue_ids = issue_ids[0].split(',')
    for issue_id in issue_ids:
        request_body = request_body + '&id=' + issue_id
    return request_body


def get_first_index(from_list: list, err):
    if len(from_list) > 0:
        return from_list[0]
    else:
        raise IndexError(err)


dataset = datasets()
resources = read_json(file_json='locustio/resources.json')