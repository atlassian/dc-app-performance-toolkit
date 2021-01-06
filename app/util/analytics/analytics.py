import sys
import requests
import uuid
from datetime import datetime, timezone

from util.analytics.application_info import ApplicationSelector, BaseApplication
from util.analytics.log_reader import BztFileReader, ResultsFileReader
from util.conf import TOOLKIT_VERSION
from util.analytics.analytics_utils import get_os, convert_to_sec, get_timestamp, get_date, is_all_tests_successful, \
    uniq_user_id, generate_report_summary, get_first_elem, generate_test_actions_by_type

JIRA = 'jira'
CONFLUENCE = 'confluence'
BITBUCKET = 'bitbucket'
JSM = 'jsm'

MIN_DEFAULTS = {JIRA: {'test_duration': 2700, 'concurrency': 200},
                CONFLUENCE: {'test_duration': 2700, 'concurrency': 200},
                BITBUCKET: {'test_duration': 3000, 'concurrency': 20, 'git_operations_per_hour': 14400},
                JSM: {'test_duration': 2700, 'customer_concurrency': 150, 'agent_concurrency': 50}
                }

BASE_URL = 'https://s7hdm2mnj1.execute-api.us-east-2.amazonaws.com/default/analytics_collector'
SUCCESS_TEST_RATE = 95.00


class AnalyticsCollector:

    def __init__(self, application: BaseApplication):
        bzt_log = BztFileReader()

        self.log_dir = bzt_log.log_dir
        self.conf = application.config
        self.app_type = application.type
        self.results_log = ResultsFileReader()
        self.run_id = str(uuid.uuid1())
        self.tool_version = TOOLKIT_VERSION
        self.os = get_os()
        self.duration = convert_to_sec(self.conf.duration)
        self.concurrency = self.conf.concurrency
        self.actual_duration = bzt_log.actual_run_time
        self.test_actions_success_rate, self.test_actions_avg_rate = bzt_log.all_test_actions

        self.selenium_test_rates, self.jmeter_test_rates, self.locust_test_rates, self.app_specific_rates = \
            generate_test_actions_by_type(test_actions=self.test_actions_success_rate, application=application)
        self.time_stamp = get_timestamp()
        self.date = get_date()
        self.application_version = application.version
        self.nodes_count = application.nodes_count
        self.dataset_information = application.dataset_information

    def is_analytics_enabled(self):
        return str(self.conf.analytics_collector).lower() in ['yes', 'true', 'y']

    def set_date_timestamp(self):
        utc_now = datetime.utcnow()
        self.time_stamp = int(round(utc_now.timestamp() * 1000))
        self.date = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat('T', 'seconds')

    def is_success(self):
        message = 'OK'
        load_test_rates = dict()
        if self.conf.load_executor == 'jmeter':
            load_test_rates = self.jmeter_test_rates
        elif self.conf.load_executor == 'locust':
            load_test_rates = self.locust_test_rates
        if not load_test_rates:
            return False, f"Jmeter/Locust test results was not found."

        if not self.selenium_test_rates:
            return False, f"Selenium test results was not found."

        success = (is_all_tests_successful(load_test_rates) and
                   is_all_tests_successful(self.selenium_test_rates))

        if not success:
            message = f"One or more actions have success rate < {SUCCESS_TEST_RATE} %."
        return success, message

    def is_finished(self):
        message = 'OK'
        finished = self.actual_duration >= self.duration
        if not finished:
            message = (f"Actual test duration {self.actual_duration} sec "
                       f"< than expected test_duration {self.duration} sec.")
        return finished, message

    def is_compliant(self):
        message = 'OK'

        if self.app_type == JSM:
            compliant = (self.actual_duration >= MIN_DEFAULTS[self.app_type]['test_duration'] and
                         self.concurrency >= MIN_DEFAULTS[self.app_type]['customer_concurrency']
                         + MIN_DEFAULTS[self.app_type]['agent_concurrency'])
        else:
            compliant = (self.actual_duration >= MIN_DEFAULTS[self.app_type]['test_duration'] and
                         self.concurrency >= MIN_DEFAULTS[self.app_type]['concurrency'])

        if not compliant:
            err_msg = []
            if self.actual_duration < MIN_DEFAULTS[self.app_type]['test_duration']:
                err_msg.append(f"Test run duration {self.actual_duration} sec < than minimum test "
                               f"duration {MIN_DEFAULTS[self.app_type]['test_duration']} sec.")
                if self.app_type == JSM:
                    min_default_concurrency = MIN_DEFAULTS[JSM]['customer_concurrency'] + \
                                              MIN_DEFAULTS[JSM]['agent_concurrency']
                    if self.concurrency < min_default_concurrency:
                        err_msg.append(f"Total test run concurrency {self.concurrency} < than minimum required test "
                                       f"concurrency: agent_concurrency={MIN_DEFAULTS[JSM]['agent_concurrency']} and "
                                       f"customer_concurrency={MIN_DEFAULTS[JSM]['customer_concurrency']}")
                else:
                    if self.concurrency < MIN_DEFAULTS[self.app_type]['concurrency']:
                        err_msg.append(f"Test run concurrency {self.concurrency} < than minimum test "
                                       f"concurrency {MIN_DEFAULTS[self.app_type]['concurrency']}.")
            message = ' '.join(err_msg)
        return compliant, message

    def is_git_operations_compliant(self):
        # calculate expected git operations for a particular test duration
        message = 'OK'
        expected_get_operations_count = int(MIN_DEFAULTS[BITBUCKET]['git_operations_per_hour'] / 3600 * self.duration)
        git_operations_compliant = self.results_log.actual_git_operations_count >= expected_get_operations_count
        if not git_operations_compliant:
            message = (f"Total git operations {self.results_log.actual_git_operations_count} < than "
                       f"{expected_get_operations_count} - minimum for expected duration {self.duration} sec.")
        return git_operations_compliant, message


def send_analytics(collector: AnalyticsCollector):
    headers = {"Content-Type": "application/json"}
    payload = {"run_id": collector.run_id,
               "user_id": uniq_user_id(collector.conf.server_url),
               "app_version": collector.application_version,
               "date": collector.date,
               "time_stamp": collector.time_stamp,
               "app_type": collector.app_type,
               "os": collector.os,
               "tool_ver": collector.tool_version,
               "exp_dur": collector.duration,
               "act_dur": collector.actual_duration,
               "selenium_test_rates": collector.selenium_test_rates,
               "jmeter_test_rates": collector.jmeter_test_rates,
               "locust_test_rates": collector.locust_test_rates,
               "concurrency": collector.concurrency
               }
    r = requests.post(url=f'{BASE_URL}', json=payload, headers=headers)
    print(r.json())
    if r.status_code != 200:
        print(f'Warning: Analytics data was send unsuccessfully, status code {r.status_code}')


def main():
    application_name = get_first_elem(sys.argv)
    application = ApplicationSelector(application_name).application
    collector = AnalyticsCollector(application)
    generate_report_summary(collector)
    if collector.is_analytics_enabled():
        send_analytics(collector)


if __name__ == '__main__':
    main()
