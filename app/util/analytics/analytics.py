import sys
import uuid

import requests
from util.data_preparation.prepare_data_common import __warnings_filter

from util.analytics.analytics_utils import get_os, convert_to_sec, get_timestamp, get_date, is_all_tests_successful, \
    uniq_user_id, generate_report_summary, get_first_elem, generate_test_actions_by_type, get_crowd_sync_test_results
from util.analytics.application_info import ApplicationSelector, BaseApplication, JIRA, CONFLUENCE, BITBUCKET, JSM, \
    CROWD, BAMBOO, INSIGHT
from util.analytics.bamboo_post_run_collector import BambooPostRunCollector
from util.analytics.log_reader import BztFileReader, ResultsFileReader, LocustFileReader
from util.conf import TOOLKIT_VERSION

__warnings_filter()

MIN_DEFAULTS = {JIRA: {'test_duration': 2700, 'concurrency': 200},
                CONFLUENCE: {'test_duration': 2700, 'concurrency': 200},
                BITBUCKET: {'test_duration': 3000, 'concurrency': 20, 'git_operations_per_hour': 14400},
                JSM: {'test_duration': 2700, 'customer_concurrency': 150, 'agent_concurrency': 50},
                CROWD: {'test_duration': 2700, 'concurrency': 1000},
                BAMBOO: {'test_duration': 2700, 'concurrency': 200, 'parallel_plans_count': 40},
                INSIGHT: {'test_duration': 2700, 'customer_concurrency': 150, 'agent_concurrency': 50}
                }
CROWD_RPS = {'server': 50, 1: 50, 2: 100, 4: 200}  # Crowd requests per second for 1,2,4 nodes.

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
        self.test_actions_success_rate, self.test_actions_timing = self.results_log.all_tests_actions

        self.selenium_test_rates, self.jmeter_test_rates, self.locust_test_rates, self.app_specific_rates = \
            generate_test_actions_by_type(test_actions=self.test_actions_success_rate, application=application)
        self.time_stamp = get_timestamp()
        self.date = get_date()
        self.application_version = application.version
        self.nodes_count = application.nodes_count
        self.dataset_information = application.dataset_information
        if self.app_type != CROWD:
            self.processors = application.processors
            self.deployment = application.deployment
        # JSM(INSIGHT) app type has additional concurrency fields: concurrency_agents, concurrency_customers
        if self.app_type == INSIGHT:
            self.concurrency_agents = self.conf.agents_concurrency
            self.concurrency_customers = self.conf.customers_concurrency
            self.insight = self.conf.insight
        if self.app_type == JSM:
            self.concurrency_agents = self.conf.agents_concurrency
            self.concurrency_customers = self.conf.customers_concurrency
            self.insight = self.conf.insight
        if self.app_type == CROWD:
            self.crowd_sync_test = get_crowd_sync_test_results(bzt_log)
            self.ramp_up = application.config.ramp_up
            self.total_actions_per_hour = application.config.total_actions_per_hour
            self.deployment = 'other'
        if self.app_type == BAMBOO:
            self.parallel_plans_count = application.config.parallel_plans_count
            self.locust_log = LocustFileReader()
            self.post_run_collector = BambooPostRunCollector(self.locust_log)
        if self.app_type == CONFLUENCE:
            self.java_version = application.java_version

    def is_analytics_enabled(self):
        """
        Check if analytics is enabled in *.yml file.
        """
        return str(self.conf.analytics_collector).lower() in ['yes', 'true', 'y']

    def is_success(self):
        """
        Verify that tests are found and the success rate of the test actions of the run(minimum success rate 95% for
        tests).

        :return: True with “OK” message if all tests >=95% success, otherwise False with an explanatory message.
        """
        message = 'OK'
        load_test_rates = dict()
        if self.conf.load_executor == 'jmeter':
            load_test_rates = self.jmeter_test_rates
        elif self.conf.load_executor == 'locust':
            load_test_rates = self.locust_test_rates
        if not load_test_rates:
            return False, f"Jmeter/Locust test results was not found."

        # There are no selenium tests for Crowd
        if self.app_type != CROWD:
            if not self.selenium_test_rates:
                return False, f"Selenium test results was not found."

        success = (is_all_tests_successful(load_test_rates) and
                   is_all_tests_successful(self.selenium_test_rates))

        if not success:
            message = f"One or more actions have success rate < {SUCCESS_TEST_RATE} %."
        return success, message

    def is_finished(self):
        """
        Verify that the required duration matches the default requirements for each product
        (e.g. of default duration Confluence 45m, Bitbucket 50m).

        :return: True with "OK" message if the run duration is correct, otherwise False with an explanatory message.
        """
        message = 'OK'
        finished = self.actual_duration >= self.duration
        if not finished:
            message = (f"Actual test duration {self.actual_duration} sec "
                       f"< than expected test_duration {self.duration} sec.")
        return finished, message

    def is_compliant(self):
        """
        Check if the values (duration/concurrency etc.) set up for the run (in *.yml)
        meet the default minimum requirements for each product.

        :return: True with "OK" message if the result compliant, otherwise False with an explanatory message.
        """
        message = 'OK'

        if self.app_type == JSM:
            compliant = (self.actual_duration >= MIN_DEFAULTS[self.app_type]['test_duration'] and
                         self.concurrency_customers >= MIN_DEFAULTS[self.app_type]['customer_concurrency'] and
                         self.concurrency_agents >= MIN_DEFAULTS[self.app_type]['agent_concurrency'])
        elif self.app_type == INSIGHT:
            compliant = (self.actual_duration >= MIN_DEFAULTS[self.app_type]['test_duration'] and
                         self.concurrency_customers >= MIN_DEFAULTS[self.app_type]['customer_concurrency'] and
                         self.concurrency_agents >= MIN_DEFAULTS[self.app_type]['agent_concurrency'])
        elif self.app_type == CROWD:
            rps_compliant = CROWD_RPS[self.nodes_count]
            total_actions_compliant = rps_compliant * 3600
            ramp_up_compliant = MIN_DEFAULTS[CROWD]['concurrency'] / rps_compliant
            ramp_up = convert_to_sec(self.ramp_up)
            compliant = (ramp_up >= ramp_up_compliant and self.total_actions_per_hour >= total_actions_compliant and
                         self.actual_duration >= MIN_DEFAULTS[self.app_type]['test_duration'])
        elif self.app_type == BAMBOO:
            compliant = (self.actual_duration >= MIN_DEFAULTS[self.app_type]['test_duration'] and
                         self.concurrency >= MIN_DEFAULTS[self.app_type]['concurrency'] and
                         self.parallel_plans_count >= MIN_DEFAULTS[self.app_type]['parallel_plans_count'])
        else:
            compliant = (self.actual_duration >= MIN_DEFAULTS[self.app_type]['test_duration'] and
                         self.concurrency >= MIN_DEFAULTS[self.app_type]['concurrency'])

        if not compliant:
            err_msg = []
            if self.actual_duration < MIN_DEFAULTS[self.app_type]['test_duration']:
                err_msg.append(f"Test run duration {self.actual_duration} sec < than minimum test "
                               f"duration {MIN_DEFAULTS[self.app_type]['test_duration']} sec.")

            if self.app_type == JSM:
                if self.concurrency_customers < MIN_DEFAULTS[JSM]['customer_concurrency']:
                    err_msg.append(f"The concurrency_customers = {self.concurrency_customers} is less than "
                                   f"required value {MIN_DEFAULTS[JSM]['customer_concurrency']}.")
                if self.concurrency_agents < MIN_DEFAULTS[JSM]['agent_concurrency']:
                    err_msg.append(f"The concurrency_agents = {self.concurrency_agents} is less than "
                                   f"required value {MIN_DEFAULTS[JSM]['agent_concurrency']}.")

            elif self.app_type == INSIGHT:
                if self.concurrency_customers < MIN_DEFAULTS[INSIGHT]['customer_concurrency']:
                    err_msg.append(f"The concurrency_customers = {self.concurrency_customers} is less than "
                                   f"required value {MIN_DEFAULTS[INSIGHT]['customer_concurrency']}.")
                if self.concurrency_agents < MIN_DEFAULTS[JSM]['agent_concurrency']:
                    err_msg.append(f"The concurrency_agents = {self.concurrency_agents} is less than "
                                   f"required value {MIN_DEFAULTS[INSIGHT]['agent_concurrency']}.")

            elif self.app_type == BAMBOO:
                if self.actual_duration < MIN_DEFAULTS[self.app_type]['test_duration']:
                    err_msg.append(f"The actual test duration {self.actual_duration} is less than "
                                   f"required value {MIN_DEFAULTS[self.app_type]['test_duration']}")
                if self.concurrency < MIN_DEFAULTS[self.app_type]['concurrency']:
                    err_msg.append(f"The run concurrency {self.concurrency} is less "
                                   f"than minimum concurrency "
                                   f"required {MIN_DEFAULTS[self.app_type]['concurrency']}")
                if self.parallel_plans_count < MIN_DEFAULTS[self.app_type]['parallel_plans_count']:
                    err_msg.append(f"The parallel_plans_count {self.parallel_plans_count} is less "
                                   f"than minimum parallel_plans_count value "
                                   f"required {MIN_DEFAULTS[self.app_type]['parallel_plans_count']}")

            elif self.app_type == CROWD:
                if ramp_up < ramp_up_compliant:
                    err_msg.append(f"The run ramp-up {ramp_up} is less than minimum ramp-up "
                                   f"required for the {self.nodes_count} nodes {ramp_up_compliant}")
                if self.total_actions_per_hour < total_actions_compliant:
                    err_msg.append(f"The run total_actions_per_hour {self.total_actions_per_hour} is less "
                                   f"than minimum total_actions_per_hour "
                                   f"required for the {self.nodes_count} nodes {total_actions_compliant}")

            else:
                if self.concurrency < MIN_DEFAULTS[self.app_type]['concurrency']:
                    err_msg.append(f"Test run concurrency {self.concurrency} < than minimum test "
                                   f"concurrency {MIN_DEFAULTS[self.app_type]['concurrency']}.")
            message = ' '.join(err_msg)
        return compliant, message

    def is_git_operations_compliant(self):
        """
        Calculate expected git operations for a given test duration (only for BITBUCKET).

        :return: True with "OK" message if the result matches the requirements,
                 otherwise False with an explanatory message.
        """
        message = 'OK'
        expected_get_operations_count = int(MIN_DEFAULTS[BITBUCKET]['git_operations_per_hour'] / 3600 * self.duration)
        git_operations_compliant = self.results_log.actual_git_operations_count >= expected_get_operations_count
        if not git_operations_compliant:
            message = (f"Total git operations {self.results_log.actual_git_operations_count} < than "
                       f"{expected_get_operations_count} - minimum for expected duration {self.duration} sec.")
        return git_operations_compliant, message


def send_analytics(collector: AnalyticsCollector):
    """
    Send Analytics data to AWS.

    :param collector: Collecting all the data from the run.
    """
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
               "concurrency": collector.concurrency,
               "deployment": collector.deployment
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
