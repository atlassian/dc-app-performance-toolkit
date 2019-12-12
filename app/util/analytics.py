import sys
import os
import re
import requests
from datetime import datetime
import platform
import uuid
import json
from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, TOOLKIT_VERSION

JIRA = 'jira'
CONFLUENCE = 'confluence'
BITBUCKET = 'bitbucket'
SUCCESS_TEST_RATE = 95.00
# List in value in case of specific output appears for some OS for command platform.system()
OS = {'macOS': ['Darwin'], 'Windows': ['Windows'], 'Linux': ['Linux']}
DT_REGEX = r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})'
SUCCESS_TEST_RATE_REGX = r'(\d{1,3}.\d{1,2}%)'
JMETER_TEST_REGX = r'jmeter_\S*'
SELENIUM_TEST_REGX = r'selenium_\S*'
BASE_URL = 'https://s7hdm2mnj1.execute-api.us-east-2.amazonaws.com/default/analytics_collector'


APP_TYPE_MSG = 'Please run util/analytics.py with application type as argument. E.g. python util/analytics.py jira'


def __validate_app_type():
    try:
        app_type = sys.argv[1]
        if app_type.lower() not in [JIRA, CONFLUENCE, BITBUCKET]:
            raise SystemExit(APP_TYPE_MSG)
    except IndexError:
        SystemExit(APP_TYPE_MSG)


def get_application_type():
    __validate_app_type()
    return sys.argv[1]


class AnalyticsCollector:

    def __init__(self, application_type):
        self.application_type = application_type
        self.run_id = str(uuid.uuid1())
        self.application_url = ""
        self.tool_version = ""
        self.os = ""
        self.duration = 0
        self.concurrency = 0
        self.actual_duration = 0
        self.selenium_test_count = 0
        self.jmeter_test_count = 0
        self.time_stamp = ""
        self.date = ""

    @property
    def config_yml(self):
        if self.application_type.lower() == JIRA:
            return JIRA_SETTINGS
        if self.application_type.lower() == CONFLUENCE:
            return CONFLUENCE_SETTINGS
        # TODO Bitbucket the same approach

    @property
    def _log_dir(self):
        if 'TAURUS_ARTIFACTS_DIR' in os.environ:
            return os.environ.get('TAURUS_ARTIFACTS_DIR')
        else:
            raise SystemExit('Taurus result directory could not be found')

    @property
    def bzt_log_file(self):
        with open(f'{self._log_dir}/bzt.log') as log_file:
            log_file = log_file.readlines()
            return log_file

    @staticmethod
    def get_os():
        os_type = platform.system()
        for key, value in OS.items():
            os_type = key if os_type in value else os_type
        return os_type

    def is_analytics_enabled(self):
        return str(self.config_yml.analytics_collector).lower() in ['yes', 'true', 'y']

    def __validate_bzt_log_not_empty(self):
        if len(self.bzt_log_file) == 0:
            raise SystemExit(f'bzt.log file in {self._log_dir} is empty')

    def get_duration_by_start_finish_strings(self):
        first_string = self.bzt_log_file[0]
        last_string = self.bzt_log_file[-1]
        start_time = re.findall(DT_REGEX, first_string)[0]
        start_datetime_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        finish_time = re.findall(DT_REGEX, last_string)[0]
        finish_datetime_obj = datetime.strptime(finish_time, '%Y-%m-%d %H:%M:%S')
        duration = finish_datetime_obj - start_datetime_obj
        return duration.seconds

    def get_duration_by_test_duration(self):
        test_duration = None
        for string in self.bzt_log_file:
            if 'Test duration' in string:
                str_duration = string.split('duration:')[1].replace('\n', '')
                str_duration = str_duration.replace(' ', '')
                duration_datetime_obj = datetime.strptime(str_duration, '%H:%M:%S')
                test_duration = (duration_datetime_obj.hour*3600 +
                                 duration_datetime_obj.minute*60 + duration_datetime_obj.second)
                break
        return test_duration

    def get_actual_run_time(self):
        self.__validate_bzt_log_not_empty()
        run_time_bzt = self.get_duration_by_test_duration()
        run_time_start_finish = self.get_duration_by_start_finish_strings()
        return run_time_bzt if run_time_bzt else run_time_start_finish

    @staticmethod
    def get_test_count_by_type(tests_type, log):
        trigger = f' {tests_type}_'
        test_search_regx = ""
        if tests_type == 'jmeter':
            test_search_regx = JMETER_TEST_REGX
        elif tests_type == 'selenium':
            test_search_regx = SELENIUM_TEST_REGX
        tests = {}
        for line in log:
            if trigger in line and ('FAIL' in line or 'OK' in line):
                test_name = re.findall(test_search_regx, line)[0]
                test_rate = float(''.join(re.findall(SUCCESS_TEST_RATE_REGX, line))[:-1])
                if test_name not in tests:
                    tests[test_name] = test_rate
        return tests

    def set_actual_test_count(self):
        test_result_string_trigger = 'Request label stats:'
        res_string_idx = [index for index, value in enumerate(self.bzt_log_file) if test_result_string_trigger in value]
        # Cut bzt.log from the 'Request label stats:' string to the end
        if res_string_idx:
            res_string_idx = res_string_idx[0]
            results_bzt_run = self.bzt_log_file[res_string_idx:]

            self.selenium_test_count = self.get_test_count_by_type(tests_type='selenium', log=results_bzt_run)
            self.jmeter_test_count = self.get_test_count_by_type(tests_type='jmeter', log=results_bzt_run)

    @staticmethod
    def __convert_to_sec(duration):
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        duration = str(duration)
        numbers = ''.join(filter(str.isdigit, duration))
        units = ''.join(filter(str.isalpha, duration))
        return int(numbers) * seconds_per_unit[units] if units in seconds_per_unit else int(numbers)

    def set_date_timestamp(self):
        utc_now = datetime.utcnow()
        self.time_stamp = int(round(utc_now.timestamp() * 1000))
        self.date = utc_now.strftime("%m/%d/%Y-%H:%M:%S")

    def generate_analytics(self):
        self.application_url = self.config_yml.server_url
        self.concurrency = self.config_yml.concurrency
        self.duration = self.__convert_to_sec(self.config_yml.duration)
        self.os = self.get_os()
        self.actual_duration = self.get_actual_run_time()
        self.tool_version = TOOLKIT_VERSION
        self.set_actual_test_count()
        self.set_date_timestamp()


class AnalyticsSender:

    def __init__(self, analytics_instance):
        self.analytics = analytics_instance

    def send_request(self):
        headers = {"Content-Type": "application/json"}
        payload = {"run_id": self.analytics.run_id,
                   "date": self.analytics.date,
                   "time_stamp": self.analytics.time_stamp,
                   "app_type": self.analytics.application_type,
                   "os": self.analytics.os,
                   "tool_ver": self.analytics.tool_version,
                   "exp_dur": self.analytics.duration,
                   "act_dur":  self.analytics.actual_duration,
                   "full_selenium": self.analytics.selenium_test_count,
                   "full_jmeter": self.analytics.jmeter_test_count,
                   "concurrency": self.analytics.concurrency
        }
        r = requests.post(url=f'{BASE_URL}', json=payload, headers=headers)
        print(r.json())
        if r.status_code != 200:
            print(f'Analytics data was send unsuccessfully, status code {r.status_code}')


def main():
    app_type = get_application_type()
    collector = AnalyticsCollector(app_type)
    if collector.is_analytics_enabled():
        collector.generate_analytics()
        sender = AnalyticsSender(collector)
        sender.send_request()


if __name__ == '__main__':
    main()

