import os
import platform
import hashlib
import getpass
import socket
from datetime import datetime, timezone

SUCCESS_TEST_RATE = 95.00
SUCCESS_AVG_RT = 20
OS = {'macOS': ['Darwin'], 'Windows': ['Windows'], 'Linux': ['Linux']}
APP_SPECIFIC_TAG = 'APP-SPECIFIC'

# Add an exception to these actions because of long time execution
EXCEPTIONS = ['jmeter_clone_repo_via_http', 'jmeter_clone_repo_via_ssh', 'selenium_create_pull_request']


def is_docker():
    path = '/proc/self/cgroup'
    return (
            os.path.exists('/.dockerenv') or
            os.path.isfile(path) and any('docker' in line for line in open(path))
    )


def format_string_summary_report(string_to_format, offset_1st=50, offset=20):
    # format string with delimiter "|"
    result = ''
    for i, item in enumerate(string_to_format.split("|")):
        if i == 0:
            off = offset_1st
        else:
            # Set 50 spaces after first column and 20 spaces after second+ column
            off = offset
        result = result + f'{item}{" " * (off - len(str(item)))}'
    result = result + '\n'
    return result


def write_to_file(content, file):
    with open(file, 'w') as f:
        f.writelines(content)


def generate_report_summary(collector):
    bitbucket = 'bitbucket'
    git_compliant = None

    summary_report = []
    summary_report_file = f'{collector.log_dir}/results_summary.log'

    finished = collector.is_finished()
    compliant = collector.is_compliant()
    success = collector.is_success()

    overall_status = 'OK' if finished[0] and success[0] and compliant[0] else 'FAIL'

    if collector.app_type == bitbucket:
        git_compliant = collector.is_git_operations_compliant()
        overall_status = 'OK' if finished[0] and success[0] and compliant[0] and git_compliant[0] else 'FAIL'

    summary_report.append(f'Summary run status|{overall_status}\n')
    summary_report.append(f'Artifacts dir|{os.path.basename(collector.log_dir)}')
    summary_report.append(f'OS|{collector.os}')
    summary_report.append(f'DC Apps Performance Toolkit version|{collector.tool_version}')
    summary_report.append(f'Application|{collector.app_type} {collector.application_version}')
    summary_report.append(f'Dataset info|{collector.dataset_information}')
    summary_report.append(f'Application nodes count|{collector.nodes_count}')
    summary_report.append(f'Concurrency|{collector.concurrency}')
    summary_report.append(f'Expected test run duration from yml file|{collector.duration} sec')
    summary_report.append(f'Actual test run duration|{collector.actual_duration} sec')

    if collector.app_type == bitbucket:
        total_git_count = collector.results_log.actual_git_operations_count
        summary_report.append(f'Total Git operations count|{total_git_count}')
        summary_report.append(f'Total Git operations compliant|{git_compliant}')

    summary_report.append(f'Finished|{finished}')
    summary_report.append(f'Compliant|{compliant}')
    summary_report.append(f'Success|{success}')
    summary_report.append(f'Has app-specific actions|{bool(collector.app_specific_rates)}')

    summary_report.append('\nAction|Success Rate|Avg time|Status')
    load_test_rates = collector.jmeter_test_rates or collector.locust_test_rates

    for key, value in {**load_test_rates, **collector.selenium_test_rates}.items():
        status = 'OK' if value >= SUCCESS_TEST_RATE else 'Fail'
        avg_rt_status = None
        if status != 'Fail' and key not in EXCEPTIONS and collector.test_actions_avg_rate[key] >= SUCCESS_AVG_RT:
            avg_rt_status = f'WARNING - action timing >= {SUCCESS_AVG_RT} sec. Check your configuration.'
        summary_report.append(f'{key}|{value}|{collector.test_actions_avg_rate[key]}|{avg_rt_status or status}')

    for key, value in collector.app_specific_rates.items():
        status = 'OK' if value >= SUCCESS_TEST_RATE else 'Fail'
        summary_report.append(f'{key}|{value}|{collector.test_actions_avg_rate[key]}|{status}|{APP_SPECIFIC_TAG}')

    max_summary_report_str_len = len(max({**load_test_rates, **collector.selenium_test_rates}.keys(), key=len))
    offset_1st = max_summary_report_str_len + 5

    pretty_report = map(lambda x: format_string_summary_report(x, offset_1st), summary_report)
    write_to_file(pretty_report, summary_report_file)


def get_os():
    os_type = platform.system()
    for key, value in OS.items():
        os_type = key if os_type in value else os_type
    return os_type


def uniq_user_id(server_url: str):
    if is_docker():
        user_info = server_url
    else:
        user_info = str(platform.node()) + str(getpass.getuser()) + str(socket.gethostname())
    uid = hashlib.pbkdf2_hmac('sha256', user_info.encode('utf-8'),
                              b"DCAPT Centaurus",
                              100000).hex()
    return uid


def convert_to_sec(duration):
    seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    duration = str(duration)
    numbers = ''.join(filter(str.isdigit, duration))
    units = ''.join(filter(str.isalpha, duration))
    return int(numbers) * seconds_per_unit[units] if units in seconds_per_unit else int(numbers)


def is_all_tests_successful(tests: dict):
    for test_stats in tests.values():
        if test_stats < SUCCESS_TEST_RATE:
            return False
    return True


def get_first_elem(elems: list):
    try:
        return elems[1]
    except IndexError:
        raise Exception('analytics.py expects application name as argument')


def get_date():
    date = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat('T', 'seconds')
    return date


def get_timestamp():
    utc_now = datetime.utcnow()
    time_stamp = int(round(utc_now.timestamp() * 1000))
    return time_stamp


def generate_test_actions_by_type(test_actions, application):
    selenium_actions = {}
    jmeter_actions = {}
    locust_actions = {}
    app_specific_actions = {}
    for test_action, value in test_actions.items():
        if test_action in application.selenium_default_actions:
            selenium_actions.setdefault(test_action, value)
        elif application.type != 'bitbucket' and test_action in application.locust_default_actions:
            locust_actions.setdefault(test_action, value)
        elif test_action in application.jmeter_default_actions:
            jmeter_actions.setdefault(test_action, value)
        else:
            app_specific_actions.setdefault(test_action, value)
    return selenium_actions, jmeter_actions, locust_actions, app_specific_actions
