import sys
import os
import re
import requests
from datetime import datetime
import hashlib
import platform

from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, TOOLKIT_VERSION

JIRA = 'jira'
CONFLUENCE = 'confluence'
BITBUCKET = 'bitbucket'
# List in value in case of specific output appears for some OS for command platform.system()
OS = {'macOS': ['Darwin'], 'Windows': ['Windows'], 'Linux': ['Linux']}
DT_REGEX = r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})'

BASE_URL = 'http://dcapps-ua-test.s3.us-east-2.amazonaws.com/stats.html?'
DEV_BASE_URL = 'http://dcapps-ua-test.s3.us-east-2.amazonaws.com/stats_dev.html?'

APP_TYPE_MSG = 'Please run util/analytics.py with application type as argument. E.g. python util/analytics.py jira'


def __validate_app_type():
    try:
        app_type = sys.argv[1]
        if app_type.lower() not in [JIRA, CONFLUENCE, BITBUCKET]:
            raise SystemExit(APP_TYPE_MSG)
    except IndexError:
        SystemExit(APP_TYPE_MSG)


def application_type():
    __validate_app_type()
    return sys.argv[1]


class AnalyticsFormer:

    def __init__(self, application_type):
        self.application_type = application_type
        self.run_id = ""
        self.application_url = ""
        self.tool_version = ""
        self.os = ""
        self.duration = 0
        self.concurrency = 0
        self.actual_duration = 0
        self.selenium_test_count = 0
        self.jmeter_test_count = 0

    @property
    def config_yml(self):
        if self.application_type.lower() == JIRA:
            return JIRA_SETTINGS
        if self.application_type.lower() == CONFLUENCE:
            return CONFLUENCE_SETTINGS
        # TODO Bitbucket the same approach

    @property
    def __last_log_dir(self):
        if 'TAURUS_ARTIFACTS_DIR' in os.environ:
            return os.environ.get('TAURUS_ARTIFACTS_DIR')
        else:
            raise SystemExit('Taurus result directory could not be found')

    @property
    def last_bzt_log_file(self):
        with open(f'{self.__last_log_dir}/bzt.log') as log_file:
            log_file = log_file.readlines()
            return log_file

    @staticmethod
    def get_os():
        os_type = platform.system()
        for key, value in OS.items():
            os_type = key if os_type in value else os_type
        return os_type

    @staticmethod
    def id_generator(string):
        dt = datetime.now().strftime("%H%M%S%f")
        string_to_hash = str.encode(f'{dt}{string}')
        hash_str = hashlib.sha1(string_to_hash).hexdigest()
        min_hash = hash_str[:len(hash_str)//3]
        return min_hash

    def is_analytics_enabled(self):
        return str(self.config_yml.analytics_collector).lower() in ['yes', 'true', 'y']

    def __validate_bzt_log_not_empty(self):
        if len(self.last_bzt_log_file) == 0:
            raise SystemExit(f'bzt.log file in {self.__last_log_dir} is empty')

    def get_duration_by_start_finish_strings(self):
        first_string = self.last_bzt_log_file[0]
        last_string = self.last_bzt_log_file[-1]
        start_time = re.findall(DT_REGEX, first_string)[0]
        start_datetime_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        finish_time = re.findall(DT_REGEX, last_string)[0]
        finish_datetime_obj = datetime.strptime(finish_time, '%Y-%m-%d %H:%M:%S')
        duration = finish_datetime_obj - start_datetime_obj
        return duration.seconds

    def get_duration_by_test_duration(self):
        test_duration = None
        for string in self.last_bzt_log_file:
            if 'Test duration' in string:
                str_duration = string.split('duration:')[1].replace('\n', '')
                str_duration = str_duration.replace(' ', '')
                duration_datetime_obj = datetime.strptime(str_duration, '%H:%M:%S')
                test_duration = duration_datetime_obj.hour*3600 + \
                                duration_datetime_obj.minute*60 + duration_datetime_obj.second
                break
        return test_duration

    def get_actual_run_time(self):
        self.__validate_bzt_log_not_empty()
        run_time_bzt = self.get_duration_by_test_duration()
        run_time_start_finish = self.get_duration_by_start_finish_strings()
        return run_time_bzt if run_time_bzt else run_time_start_finish

    def get_actual_test_count(self):
        jmeter_test = ' jmeter_'
        selenium_test = ' selenium_'
        for line in self.last_bzt_log_file:
            if jmeter_test in line:
                self.jmeter_test_count = self.jmeter_test_count + 1
            elif selenium_test in line:
                self.selenium_test_count = self.selenium_test_count + 1

    def generate_analytics(self):
        self.application_url = self.config_yml.server_url
        self.run_id = self.id_generator(string=self.application_url)
        self.concurrency = self.config_yml.concurrency
        self.duration = self.config_yml.duration
        self.os = self.get_os()
        self.actual_duration = self.get_actual_run_time()
        self.tool_version = TOOLKIT_VERSION
        self.get_actual_test_count()


class AnalyticsSender:

    def __init__(self, analytics_instance):
        self.run_analytics = analytics_instance

    def send_request(self):
        base_url = BASE_URL
        params_string=f'app_type={self.run_analytics.application_type}&os={self.run_analytics.os}&' \
                      f'tool_ver={self.run_analytics.tool_version}&run_id={self.run_analytics.run_id}&' \
                      f'exp_dur={self.run_analytics.duration}&act_dur={self.run_analytics.actual_duration}&' \
                      f'sel_count={self.run_analytics.selenium_test_count}&jm_count={self.run_analytics.jmeter_test_count}&' \
                      f'concurrency={self.run_analytics.concurrency}'

        r = requests.get(url=f'{base_url}{params_string}')
        if r.status_code != 403:
            print(f'Analytics data was not send to Atlassian, status code {r.status_code}')


def main():
    app_type = application_type()
    p = AnalyticsFormer(app_type)
    if p.is_analytics_enabled():
        p.generate_analytics()
        sender = AnalyticsSender(p)
        sender.send_request()


if __name__ == '__main__':
    main()
