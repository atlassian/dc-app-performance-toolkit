import os
import re
from datetime import datetime
from util.project_paths import ENV_TAURUS_ARTIFACT_DIR

GIT_OPERATIONS = ['jmeter_clone_repo_via_http', 'jmeter_clone_repo_via_ssh',
                  'jmeter_git_push_via_http', 'jmeter_git_fetch_via_http',
                  'jmeter_git_push_via_ssh', 'jmeter_git_fetch_via_ssh']


class BaseFileReader:

    @staticmethod
    def validate_file_exists(path):
        if not os.path.exists(path):
            raise Exception(f'{path} does not exist')

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
    jmeter_test_regexp = r'jmeter_\S*'
    selenium_test_regexp = r'selenium_\S*'
    locust_test_regexp = r'locust_\S*'
    success_test_rate_regexp = r'(\d{1,3}.\d{1,2}%)'

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

    def _get_test_count_by_type(self, tests_type, log):
        trigger = f' {tests_type}_'
        test_search_regx = ""
        if tests_type == 'jmeter':
            test_search_regx = self.jmeter_test_regexp
        elif tests_type == 'selenium':
            test_search_regx = self.selenium_test_regexp
        elif tests_type == 'locust':
            test_search_regx = self.locust_test_regexp
        tests = {}
        for line in log:
            if trigger in line and ('FAIL' in line or 'OK' in line):
                test_name = re.findall(test_search_regx, line)[0]
                test_rate = float(''.join(re.findall(self.success_test_rate_regexp, line))[:-1])
                if test_name not in tests:
                    tests[test_name] = test_rate
        return tests

    def _get_results_bzt_log_part(self):
        test_result_string_trigger = 'Request label stats:'
        res_string_idx = [index for index, value in enumerate(self.bzt_log) if test_result_string_trigger in value]
        # Cut bzt.log from the 'Request label stats:' string to the end
        if res_string_idx:
            res_string_idx = res_string_idx[0]
            results_bzt_run = self.bzt_log[res_string_idx:]
            return results_bzt_run

    @property
    def selenium_test_rates(self):
        return self._get_test_count_by_type(tests_type='selenium', log=self.bzt_log_results_part)

    @property
    def jmeter_test_rates(self):
        return self._get_test_count_by_type(tests_type='jmeter', log=self.bzt_log_results_part)

    @property
    def locust_test_rates(self):
        return self._get_test_count_by_type(tests_type='locust', log=self.bzt_log_results_part)

    @property
    def actual_run_time(self):
        run_time_bzt = self._get_duration_by_test_duration()
        return run_time_bzt if run_time_bzt else self._get_duration_by_start_finish_strings()


class ResultsFileReader(BaseFileReader):
    header_validation = {0: 'Label', 1: '# Samples'}

    def __init__(self):
        self.results_log = self.get_results_log()

    def get_results_log(self):
        results_log_path = f'{self.log_dir}/results.csv'
        self.validate_file_exists(results_log_path)
        with open(results_log_path) as res_file:
            header = res_file.readline()
            results = res_file.readlines()
        self.validate_file_not_empty(results)
        headers_list = header.split(',')
        self.validate_headers(headers_list, self.header_validation)
        return results

    @property
    def actual_git_operations_count(self):
        count = 0
        for line in self.results_log:
            if any(s in line for s in GIT_OPERATIONS):
                count = count + int(line.split(',')[1])
        return count
