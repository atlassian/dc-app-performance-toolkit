import random
import re
import time

from locustio.bamboo.requests_params import bamboo_datasets
from locustio.common_utils import jira_measure, fetch_by_re, timestamp_int, generate_random_string, TEXT_HEADERS, \
    ADMIN_HEADERS, NO_TOKEN_HEADERS, RESOURCE_HEADERS, init_logger, JSON_HEADERS, calculate_bamboo_sleep, bamboo_measure
from util.api.bamboo_clients import BambooClient

from util.conf import BAMBOO_SETTINGS
import uuid

logger = init_logger(app_type='bamboo')
bamboo_dataset = bamboo_datasets()
url = BAMBOO_SETTINGS.server_url
api_client = BambooClient(url, BAMBOO_SETTINGS.admin_login, BAMBOO_SETTINGS.admin_password,
                          verify=BAMBOO_SETTINGS.secure)
action_time = calculate_bamboo_sleep()
PLAN_IS_NOT_STARTED_TIMEOUT = BAMBOO_SETTINGS.start_plan_timeout  # seconds


def wait_for_online_free_agent():
    sleep_time = 1
    has_free_agent = False
    attempt_to_find_agent = 0
    attempts = 90
    while not has_free_agent:
        r = api_client.get(f'{url}/rest/api/latest/agent/remote?online=True', error_msg="Could not get online agents")
        result = r.json()
        free_agents_bool = [agent['busy'] for agent in result]
        free_agents_count = free_agents_bool.count(False)
        if attempt_to_find_agent >= attempts:
            raise Exception(f'Unable to find free agents for {attempts} seconds')
        if free_agents_count > 0:
            logger.info(f'There are {free_agents_count}/{len(free_agents_bool)} free agents\n')
            has_free_agent = True
            attempt_to_find_agent = 0
        else:
            logger.info(f'Still no free agents, wait {sleep_time} seconds, attempt {attempt_to_find_agent}/{attempts}')
            time.sleep(sleep_time)
            attempt_to_find_agent = attempt_to_find_agent + 1


def run_build_plans(locust):
    start = time.time()
    session_id = str(uuid.uuid4())
    locust.cross_action_storage[session_id] = dict()
    locust.session_data_storage = locust.cross_action_storage[session_id]
    locust.session_data_storage['app'] = 'bamboo'
    user_auth = tuple(random.choice(bamboo_dataset['users']))
    build_plan = random.choice(bamboo_dataset['build_plans'])
    build_plan_id = build_plan[1]
    # client = BambooClient(BAMBOO_SETTINGS.server_url, user=user_auth[0], password=user_auth[1])
    # print(client.get_build_plan_status(plan_key=build_plan_id))
    r = locust.get(f'/rest/api/latest/plan/{build_plan_id}', auth=user_auth, catch_response=True, headers=JSON_HEADERS)
    response = r.json()
    auth_headers = r.request.headers
    plan_is_active = response['isActive']
    plan_is_building = response['isBuilding']
    plan_is_queued = plan_is_active and not plan_is_building
    plan_is_ready_to_run = not plan_is_active
    wait_for_online_free_agent()

    @bamboo_measure('1_locust_run_build_plan')
    def run_build_plan(locust):
        plan_is_running = False
        locust.post(f'/rest/api/latest/queue/{build_plan_id}', catch_response=True,
                    headers=auth_headers, auth=user_auth)

        def plan_is_building(locust):
            request = locust.get(f'/rest/api/latest/plan/{build_plan_id}',
                                 catch_response=True, headers=auth_headers)
            return request.json()['isBuilding']

        timeout = time.time() + PLAN_IS_NOT_STARTED_TIMEOUT
        warning_timeout = time.time() + PLAN_IS_NOT_STARTED_TIMEOUT / 2
        warning_reported = False

        number_of_get_status_requests = 0
        start_time_get_status_requests = time.time()

        logger.info(f'Starting plan {build_plan_id}...')
        while not plan_is_running:
            if plan_is_building(locust):
                plan_is_running = True
            number_of_get_status_requests = number_of_get_status_requests + 1
            if time.time() > timeout:
                raise Exception(f'Build plan {build_plan_id} could not started in '
                                f'{PLAN_IS_NOT_STARTED_TIMEOUT} seconds.')

            if time.time() > warning_timeout:
                if not warning_reported:
                    logger.info(f'WARNING!! PLAN {build_plan_id} CAN NOT START IN {PLAN_IS_NOT_STARTED_TIMEOUT/2} '
                                f'SECONDS.')
                    warning_reported = True

        total_time_get_status_requests = time.time() - start_time_get_status_requests
        logger.info(f'The number of get_plan_status requests is {number_of_get_status_requests}, '
                    f'it takes {total_time_get_status_requests} seconds.')
    if plan_is_ready_to_run:
        run_build_plan(locust)

    total = (time.time() - start)
    sleep_time = action_time - total if action_time > total else 0
    logger.info(f'Total functions time: {total}. Action time {action_time}'
                f'Plan {build_plan_id} is successfully started. Waiting {sleep_time}')
    #time.sleep(sleep_time)
    with open("/Users/smoroz/repos/dc-app-performance-toolkit/app/results/actions.csv", "a") as file_object:
        # Append 'hello' at the end of file
        file_object.write(f'{total},\n')
