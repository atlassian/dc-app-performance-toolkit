import random
import time

from locustio.bamboo.requests_params import bamboo_datasets
from locustio.common_utils import init_logger, JSON_HEADERS,  bamboo_measure
from util.api.bamboo_clients import BambooClient

from util.conf import BAMBOO_SETTINGS

logger = init_logger(app_type='bamboo')
bamboo_dataset = bamboo_datasets()
url = BAMBOO_SETTINGS.server_url
api_client = BambooClient(url, BAMBOO_SETTINGS.admin_login, BAMBOO_SETTINGS.admin_password,
                          verify=BAMBOO_SETTINGS.secure)
action_time = BAMBOO_SETTINGS.default_dataset_plan_duration
PLAN_IS_NOT_STARTED_TIMEOUT = BAMBOO_SETTINGS.start_plan_timeout  # seconds


def wait_for_online_free_agent():
    sleep_time = 1
    has_free_agent = False
    attempt_to_find_agent = 0
    attempts = 90
    while not has_free_agent:
        agents = api_client.get_remote_agents(online=True)
        free_agents_count = [agent['busy'] for agent in agents].count(False)
        if attempt_to_find_agent >= attempts:
            raise Exception(f'Unable to find free agents for {attempts*sleep_time} seconds')
        if free_agents_count > 0:
            logger.info(f'There are {free_agents_count}/{len(agents)} free agents\n')
            has_free_agent = True
        else:
            logger.info(f'Still no free agents, wait {sleep_time} seconds, attempt {attempt_to_find_agent}/{attempts}')
            time.sleep(sleep_time)
            attempt_to_find_agent = attempt_to_find_agent + 1


def run_build_plans(locust):
    start = time.time()
    user_auth = tuple(random.choice(bamboo_dataset['users']))
    build_plan = random.choice(bamboo_dataset['build_plans'])
    build_plan_id = build_plan[1]
    r = locust.get(f'/rest/api/latest/plan/{build_plan_id}', auth=user_auth, catch_response=True, headers=JSON_HEADERS)
    response = r.json()
    auth_headers = r.request.headers
    plan_is_active = response['isActive']
    plan_is_building = response['isBuilding']
    plan_is_queued = plan_is_active and not plan_is_building
    plan_is_ready_to_run = not plan_is_active
    wait_for_online_free_agent()

    @bamboo_measure('locust_run_build_plan')
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
                    logger.info(f'Warning!! Plan {build_plan_id} could not start in {PLAN_IS_NOT_STARTED_TIMEOUT/2} '
                                f'seconds.')
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
    time.sleep(sleep_time)
