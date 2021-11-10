import csv
import datetime
import re
from multiprocessing.pool import ThreadPool

from util.project_paths import BAMBOO_BUILD_PLANS
from util.api.bamboo_clients import BambooClient
from util.conf import BAMBOO_SETTINGS
import time
from multiprocessing import cpu_count
from util.analytics.log_reader import BztFileReader  # just to run this code to test REMOVE AFTER
pool = ThreadPool(processes=cpu_count() * 3)


def read_input_file(file_path):
    with open(file_path, 'r') as fs:
        reader = csv.reader(fs)
        return list(reader)


class BambooPostRunCollector:

    def __init__(self, bzt_log):
        self.build_plans = [build_plan[1] for build_plan in read_input_file(BAMBOO_BUILD_PLANS)]
        self.client = BambooClient(host=BAMBOO_SETTINGS.server_url,
                                   user=BAMBOO_SETTINGS.admin_login, password=BAMBOO_SETTINGS.admin_password)
        self.bzt_log = bzt_log

    # def get_all_builds_results(self):
    #     ready_builds = []
    #     all_builds_results = []
    #     for build_id in self.build_plans:
    #         build_results = self.client.get_build_plans_results(build_plan_id=build_id, max_result=100)
    #         all_builds_results.extend([build_result['planResultKey']['key'] for build_result in build_results])
    #         ready_builds.append(build_id)
    #     print(all_builds_results)
    #     print(len(all_builds_results))

    def parallel_get_all_builds_results(self):
        all_builds_results_lists = pool.map(self.client.get_build_plans_results, [i for i in self.build_plans])
        all_builds_results = [item for sublist in all_builds_results_lists for item in sublist]
        all_builds_results_ids = [build_result['planResultKey']['key'] for build_result in all_builds_results]
        # print(all_builds_results_ids)
        # print(len(all_builds_results_ids))
        return all_builds_results_ids

    def parallel_get_build_results(self):
        all_run_ids = self.parallel_get_all_builds_results()
        expanded_run_results = pool.map(self.client.get_build_plan_results, [i for i in all_run_ids])
        return expanded_run_results

    def filter_results_current_run(self):
        builds_started_in_current_run = []
        res = []

        test_start_datetime = self.bzt_log.start_bzt_run_time
        expanded_run_results = self.parallel_get_build_results()
        build_start_time_regexp = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
        for build_result in expanded_run_results:
            build_start_match = re.search(build_start_time_regexp, build_result['buildStartedTime'])
            build_start_datetime = datetime.datetime.strptime(build_start_match.group(), '%Y-%m-%dT%H:%M:%S')

            if build_result['planResultKey']['entityKey']['key'] in ['PRJ71-FSYWXON', 'PRJ46-PDUPMOS', 'PRJ20-NFMSFMG', 'PRJ99-VQQZWFW']:
                res.append(build_result)

            if build_start_datetime > test_start_datetime:
                builds_started_in_current_run.append(build_result)

        print('asd')




        print(builds_started_in_current_run)
        print(len(builds_started_in_current_run))





start = time.time()
bzt_log = BztFileReader()
post_run = BambooPostRunCollector(bzt_log)
post_run.filter_results_current_run()
#post_run.get_all_builds_results()


end = time.time()
print(f'{(end - start)} seconds')

