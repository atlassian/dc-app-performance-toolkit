import random
import time
import uuid

from locust import events

from locustio.bamboo.requests_params import bamboo_datasets, Login
from locustio.common_utils import init_logger, JSON_HEADERS, TEXT_HEADERS, bamboo_measure
from util.api.bamboo_clients import BambooClient
from util.conf import BAMBOO_SETTINGS

logger = init_logger(app_type='bamboo')
bamboo_dataset = bamboo_datasets()
url = BAMBOO_SETTINGS.server_url
api_client = BambooClient(url, BAMBOO_SETTINGS.admin_login, BAMBOO_SETTINGS.admin_password,
                          verify=BAMBOO_SETTINGS.secure)
action_time = BAMBOO_SETTINGS.default_dataset_plan_duration
PLAN_STARTED_TIMEOUT = BAMBOO_SETTINGS.start_plan_timeout  # seconds
PLAN_STATUS_REQUEST_TIMEOUT = 10
DEFAULT_DATASET_JOB_KEY = 'JB1'


def run_build_plans(locust):
    start = time.time()
    user_auth = tuple(random.choice(bamboo_dataset['users']))
    build_plan = random.choice(bamboo_dataset['build_plans'])
    build_plan_id = build_plan[1]
    r = locust.get(f'/rest/api/latest/plan/{build_plan_id}', auth=user_auth, catch_response=True, headers=JSON_HEADERS)
    response = r.json()
    auth_headers = r.request.headers
    plan_is_active = response['isActive']

    def run_build_plan(locust):
        r = locust.post(f'/rest/api/latest/queue/{build_plan_id}', catch_response=True,
                        headers=auth_headers, auth=user_auth)
        build_num = r.json()['buildNumber']
        build_job_num = f'{build_plan_id}-{DEFAULT_DATASET_JOB_KEY}-{build_num}'
        plan_is_running = False
        total_sleep_time = 0
        build_queue_duration_msec = None
        warning_reported = False
        while not plan_is_running:
            time.sleep(PLAN_STATUS_REQUEST_TIMEOUT)
            r = locust.get(f'/rest/api/latest/result/{build_job_num}',
                           catch_response=True, headers=auth_headers)
            response = r.json()
            if 'buildStartedTime' in response:
                plan_is_running = True
                build_queue_duration_msec = int(response['queueDuration'])
                logger.info(f'Plan |{build_job_num}| starts with queue duration {build_queue_duration_msec} ms. '
                            f'Build start time: {response["buildStartedTime"]}')

            if total_sleep_time >= PLAN_STARTED_TIMEOUT / 2:
                if not warning_reported:
                    logger.info(f'WARNING: Plan |{build_job_num}| could not start in {PLAN_STARTED_TIMEOUT / 2} '
                                f'seconds.')
                    warning_reported = True
                    logger.info(f'{BAMBOO_SETTINGS.server_url}/browse/{build_plan_id}')
                total_sleep_time = total_sleep_time + PLAN_STATUS_REQUEST_TIMEOUT

            if total_sleep_time >= PLAN_STARTED_TIMEOUT:
                raise Exception(f'ERROR: Build plan {build_plan_id} could not start in '
                                f'{PLAN_STARTED_TIMEOUT} seconds.')
            else:
                total_sleep_time = total_sleep_time + PLAN_STATUS_REQUEST_TIMEOUT
        return build_queue_duration_msec

    if not plan_is_active:
        try:
            build_queue_duration_sec = run_build_plan(locust)
            events.request.fire(request_type="Action",
                                name='locust_run_build_plan',
                                response_time=float(build_queue_duration_sec),
                                response_length=0,
                                response=None,
                                context=None,
                                exception=None)
        except Exception as e:
            events.request.fire(request_type="Action",
                                name='locust_run_build_plan',
                                response_time=10,
                                response_length=0,
                                response=None,
                                context=None,
                                exception=e)

    total = time.time() - start
    sleep_time = action_time - total if action_time > total else 0
    logger.info(f'Total functions time: {total}. Expected full action time {action_time}. '
                f'Plan {build_plan_id} is successfully started. Waiting {sleep_time}.\n')
    time.sleep(sleep_time)


@bamboo_measure('locust_bamboo_login')
def locust_bamboo_login(locust):
    session_id = str(uuid.uuid4())
    locust.cross_action_storage[session_id] = dict()
    locust.session_data_storage = locust.cross_action_storage[session_id]
    locust.session_data_storage['app'] = 'bamboo'

    params = Login()
    user = random.choice(bamboo_dataset["users"])
    username = user[0]
    password = user[1]

    login_body = params.login_body
    login_body['os_username'] = username
    login_body['os_password'] = password

    # login
    r = locust.post('/userlogin.action',
                    login_body,
                    TEXT_HEADERS,
                    catch_response=True)

    content = r.content.decode('utf-8')

    if 'Log Out' not in content:
        logger.error(f'Login with {username}, {password} failed: {content}')
    assert 'Log Out' in content, 'User authentication failed.'
    logger.locust_info(f'User {username} is successfully logged in')

    locust.session_data_storage['username'] = user[0]
    locust.session_data_storage['password'] = user[1]
