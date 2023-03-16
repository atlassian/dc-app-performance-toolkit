import os
import re
import time
from datetime import datetime, timedelta
import csv

import pytz

from util.project_paths import ENV_TAURUS_ARTIFACT_DIR

GIT_OPERATIONS = ['jmeter_clone_repo_via_http', 'jmeter_clone_repo_via_ssh',
                  'jmeter_git_push_via_http', 'jmeter_git_fetch_via_http',
                  'jmeter_git_push_via_ssh', 'jmeter_git_fetch_via_ssh']


class BaseFileReader:

    @staticmethod
    def validate_file_exists(path):
        if not os.path.exists(path):
            raise SystemExit(f'{path} does not exist')

    @staticmethod
    def validate_file_not_empty(file):
        if len(file) == 0:
            raise SystemExit(f'ERROR: {file} file in {file} is empty')

    @staticmethod
    def validate_headers(headers_list, validation_dict):
        for key, value in validation_dict.items():
            if headers_list[key] != value:
                raise SystemExit(f'Header validation error. '
                                 f'Actual: {headers_list[key]}, Expected: {validation_dict[key]}')

    @property
    def log_dir(self):
        return ENV_TAURUS_ARTIFACT_DIR


class BztFileReader(BaseFileReader):

    bzt_log_name = 'bzt.log'
    dt_regexp = r'(\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2})'

    def __init__(self):
        self.bzt_log = self.get_bzt_log()
        self.bzt_log_results_part = self._get_results_bzt_log_part()

    def get_bzt_log(self):
        bzt_log_path = f'{self.log_dir}/{self.bzt_log_name}'
        self.validate_file_exists(bzt_log_path)
        with open(bzt_log_path) as log_file:
            log_file = log_file.readlines()
            self.validate_file_not_empty(log_file)
            return log_file

    def _get_duration_by_start_finish_strings(self):
        first_string = self.bzt_log[0]
        last_string = self.bzt_log[-1]
        start_time = re.findall(self.dt_regexp, first_string)[0]
        start_datetime_obj = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        finish_time = re.findall(self.dt_regexp, last_string)[0]
        finish_datetime_obj = datetime.strptime(finish_time, '%Y-%m-%d %H:%M:%S')
        duration = finish_datetime_obj - start_datetime_obj
        return duration.seconds

    def _get_duration_by_test_duration(self):
        test_duration = None
        for string in self.bzt_log:
            if 'Test duration' in string:
                str_duration = string.split('duration:')[1].replace('\n', '')
                str_duration = str_duration.replace(' ', '')
                duration_datetime_obj = datetime.strptime(str_duration, '%H:%M:%S')
                test_duration = (duration_datetime_obj.hour * 3600 +
                                 duration_datetime_obj.minute * 60 + duration_datetime_obj.second)
                break
        return test_duration

    def _get_results_bzt_log_part(self):
        test_result_string_trigger = 'Request label stats:'
        res_string_idx = [index for index, value in enumerate(self.bzt_log) if test_result_string_trigger in value]
        # Cut bzt.log from the 'Request label stats:' string to the end
        if res_string_idx:
            res_string_idx = res_string_idx[0]
            results_bzt_run = self.bzt_log[res_string_idx:]
            return results_bzt_run

    @staticmethod
    def _get_all_test_actions(log):
        test_actions_success_rate = {}
        test_actions_timing = {}

        delimiters = ['|', '\x1b(0x\x1b(B']
        delimiter = None

        for line in log:
            if ('FAIL' in line or 'OK' in line) and '%' in line:
                if not delimiter:
                    try:
                        delimiter = [dlm for dlm in delimiters if dlm in line][0]
                    except SystemExit:
                        print(f"ERROR: Unknown delimiter in line: {line}. Known delimiters are {delimiters}")
                line_split = line.split(delimiter)
                test_name = line_split[1].strip(',').strip()
                test_rate = float(line_split[3].strip(',').strip().rstrip('%'))
                test_timing = float(line_split[4].strip())

                test_actions_success_rate[test_name] = test_rate
                test_actions_timing[test_name] = test_timing

        if not test_actions_success_rate:
            raise SystemExit(f"There are no test actions where found in the {ENV_TAURUS_ARTIFACT_DIR}/bzt.log file")

        return test_actions_success_rate, test_actions_timing

    @property
    def actual_run_time(self):
        run_time_bzt = self._get_duration_by_test_duration()
        return run_time_bzt if run_time_bzt else self._get_duration_by_start_finish_strings()

    @property
    def all_test_actions_bzt_log(self):
        return self._get_all_test_actions(log=self._get_results_bzt_log_part())


class ResultsFileReader(BaseFileReader):
    header_validation = {0: 'Label', 1: '# Samples'}

    def __init__(self):
        self.results_log_path = f'{self.log_dir}/results.csv'
        self.results_log = self.get_results_log()

    def get_results_log(self):
        lines = []
        if os.path.exists(self.results_log_path) and os.path.getsize(self.results_log_path) > 0:
            with open(self.results_log_path, 'r') as res_file:
                for line in csv.DictReader(res_file):
                    lines.append(line)
        else:
            raise SystemExit(f"ERROR: file {self.results_log_path} does not exist or empty.")
        headers_list = list(lines[0].keys())
        self.validate_headers(headers_list, self.header_validation)
        self.validate_file_not_empty(lines)
        return lines

    @property
    def all_tests_actions(self):
        actions_success_rate = {}
        actions_timing = {}
        for action in self.results_log:
            if action['Label'] not in actions_timing:
                actions_timing[action['Label']] = round(int(action['90% Line']) / 1000, 2)
            if action['Label'] not in actions_success_rate:
                actions_success_rate[action['Label']] = 100 - float(action['Error %'])
        return actions_success_rate, actions_timing

    @property
    def actual_git_operations_count(self):
        count = 0
        for line in self.results_log:
            if line['Label'] in GIT_OPERATIONS:
                count = count + int(line['# Samples'])
        return count


class LocustFileReader(BaseFileReader):

    locust_log_name = 'locust.log'

    def get_locust_log(self):
        locust_log_path = f'{self.log_dir}/{self.locust_log_name}'
        self.validate_file_exists(locust_log_path)
        with open(locust_log_path) as log_file:
            log_file = log_file.readlines()
            self.validate_file_not_empty(log_file)
            return log_file
