import re
import time
from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401

logger = init_logger(app_type='jira')


@jira_measure("get-users")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def get_users(locust):
    r = locust.get('/rest/skillsforjira/1/user', catch_response=True)  # call app-specific GET endpoint
    content = r.content.decode('utf-8')   # decode response content

    if not r.ok:
        logger.error(f"get-users failed")
    assert r.ok
    
    # key_pattern_example = '"key":"(.+?)"'
    # keys = re.findall(key_pattern_example, content)  # get TOKEN from response using regexp
    #logger.locust_info(f'keys: {keys}')  # log info for debug when verbose is true in jira.yml file
    if 'key' not in content:
        logger.error(f"'key' was not found in {content}")
    assert 'key' in content  # assert specific string in response content

@jira_measure("get-changed-users")
def get_changed_users(locust):
    timestamp = time.time()
    r = locust.get(f'/rest/skillsforjira/1/user/updatedAfter?{timestamp}', catch_response=False)  # call app-specific GET endpoint

    if not r.ok:
        logger.error(f"get-changed-users failed")
    assert r.ok

@jira_measure("get-user-pull-status")
def get_pull_status(locust):
    user_key = 'admin'
    r = locust.get(f'/rest/skillsforjira/1/user/updatedAfter?pull/status/{user_key}', catch_response=True)
    content = r.content.decode('utf-8')   # decode response content

    if not r.ok:
        logger.error(f"get-pull-status failed")
    assert r.ok

    enabled_pattern_example = '"enabled":"(.+?)"'
    enabled = re.findall(enabled_pattern_example, content)  # get TOKEN from response using regexp

    if 'enabled' not in content:
        logger.error(f"'enabled' was not found in {content}")
    assert 'enabled' in content  # assert specific string in response content
    
@jira_measure("pull-task")
def pull_task(locust):
    body = {}  # include parsed variables to POST request body
    headers = {'content-type': 'application/json'}
    r = locust.post('/rest/skillsforjira/1/assignments/pull', body, headers, catch_response=True)  # call app-specific POST endpoint
    content = r.content.decode('utf-8')

    if not r.ok:
        logger.error(f"pull-task failed")
    assert r.ok

    if 'enabled' not in content:
        logger.error(f"'enabled' was not found in {content}")
    assert 'enabled' in content  # assert specific string in response content
