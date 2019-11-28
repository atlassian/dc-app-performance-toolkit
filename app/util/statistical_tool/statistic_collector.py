import requests
import time
import sys
import os
import re
import yaml
from pathlib import Path
import requests
from datetime import datetime
import hashlib
import platform

from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS

JIRA = 'jira'
CONFLUENCE = 'confluence'
BITBUCKET = 'bitbucket'
# List in value in case of specific output appears for some OS for command platform.system()
OS = {'macOS': ['Darwin'], 'Windows': ['Windows'], 'Linux': ['Linux']}
DT_REGEX = r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})'

def application_type():
    return sys.argv[1]


class StatisticFormer:

    def __init__(self, application_type):
        self.application_type = application_type
        self.run_id = ""
        self.application_url = ""
        self.tool_version = ""
        self.os = ""
        self.duration = 0
        self.concurrency = 0
        self.total_test_count = 0
        self.actual_duration = 0

    @property
    def config_yml(self):
        if self.application_type.lower() == JIRA:
            return CONFLUENCE_SETTINGS
        elif self.application_type.lower() == CONFLUENCE:
            return JIRA_SETTINGS
        # TODO Bitbucket the same approach

    @property
    def last_log_dir(self):
        results_dir = f'{Path(__file__).parents[2]}/results/{self.application_type.lower()}'
        last_run_log_dir = max([os.path.join(results_dir, d) for d in
                                os.listdir(results_dir)], key=os.path.getmtime)
        return last_run_log_dir

    @property
    def last_bzt_log_file(self):
        with open(f'{self.last_log_dir}/bzt.log') as log_file:
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

    def __validate_bzt_log_not_empty(self):
        if len(self.last_bzt_log_file) == 0:
            raise sys.exit(0)

    def get_duration_by_start_finish_strings(self):
        self.__validate_bzt_log_not_empty()
        first_string = self.last_bzt_log_file[0]
        last_string = self.last_bzt_log_file[len(self.last_bzt_log_file)-1]
        start_time = re.findall(DT_REGEX, first_string)[0]
        start_datetime_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        finish_time = re.findall(DT_REGEX, last_string)[0]
        finish_datetime_obj = datetime.strptime(finish_time, '%Y-%m-%d %H:%M:%S')
        duration = finish_datetime_obj - start_datetime_obj
        return duration.seconds

    def get_duration_by_test_duration(self):
        self.__validate_bzt_log_not_empty()
        test_duration = None
        for string in self.last_bzt_log_file:
            if 'Test duration' in string:
                str_duration = string.split('duration:')[1].replace('\n', '')
                duration_datetime_obj = datetime.strptime(str_duration, ' %H:%M:%S')
                test_duration = duration_datetime_obj.hour*3600 + \
                                duration_datetime_obj.minute*60 + duration_datetime_obj.second
                break
        return test_duration

    def get_actual_run_time(self):
        run_time_bzt = self.get_actual_run_time()
        run_time_start_finish = self.get_duration_by_start_finish_strings()
        return run_time_bzt if run_time_bzt else run_time_start_finish

    def generate_statistics(self):
        self.application_url = self.config_yml.server_url
        self.run_id = self.id_generator(string=self.application_url)
        self.concurrency = self.config_yml.concurrency
        self.duration = self.config_yml.duration
        self.os = self.get_os()
        self.actual_duration = self.get_actual_run_time()
        #self.tool_version = self.config_yml.tool_version







app_type = application_type()
p = StatisticFormer(app_type)

p.generate_statistics()
print(p.application_url, p.run_id)
print(p.get_duration_by_test_duration())




# a = f'{Path(__file__).parents[2]}/jira.yml'
#
# last_dir = max([os.path.join(f'{Path(__file__).parents[2]}/results/jira',d) for d in os.listdir(f'{Path(__file__).parents[2]}/results/jira')], key=os.path.getmtime)
#
# def read_yml_file(file):
#     with file.open(mode='r') as file:
#         return yaml.load(file, Loader=yaml.FullLoader)
#
# obj = read_yml_file(Path(a))
# with open('/tmp/date.tmp', 'w') as tmp:
#     tmp.write(f"datetime: {obj['settings']['env']['datetime']}'\n'   last_res_dir: {str(last_dir)}  ")
#
#



# p = StatisticPerformer(application_type=application_type())
# print(p.config_yaml)




#
#
# BASE_URL = 'http://dcapps-ua-test.s3.us-east-2.amazonaws.com/stats.html?'
# ARGS_STRING = 'user_ip=ip&run_id=run_id&start_time=start_time&end_time=end_time&version=cent_version&os=mac&duration=dur&concurrency=200&total_test_count=20'
#
#
#
# while True:
#     print(application_type())
#     r = requests.get(url=f'{BASE_URL}{ARGS_STRING}')
#     time.sleep(2)
#     print(str(r.iter_content))
