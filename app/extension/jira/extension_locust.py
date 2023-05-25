import re
import time

from locustio.common_utils import init_logger, jira_measure, run_as_specific_user  # noqa F401

from locust import HttpUser, task, between, run_single_user
from extension.bamboo.extension_locust import app_specific_action
from locustio.bamboo.http_actions import locust_bamboo_login
from locustio.common_utils import LocustConfig, MyBaseTaskSet
from util.conf import BAMBOO_SETTINGS

config = LocustConfig(config_yml=BAMBOO_SETTINGS)
logger = init_logger(app_type='jira')


class BambooBehavior(MyBaseTaskSet):
    def on_start(self):
        self.client.verify = config.secure
        locust_bamboo_login(self)

    @task(config.percentage('standalone_extension_locust'))
    @jira_measure("get-users")
    # @run_as_specific_user(username='admin', password='admin')  # run as specific user
    def get_users(self):
        r = self.get('/rest/skillsforjira/1/user', catch_response=True)  # call app-specific GET endpoint
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

    @task(config.percentage('standalone_extension_locust'))
    @jira_measure("get-changed-users")
    def get_changed_users(self):
        timestamp = time.time()
        r = self.get(f'/rest/skillsforjira/1/user/updatedAfter?{timestamp}', catch_response=False)  # call app-specific GET endpoint
    
        if not r.ok:
            logger.error(f"get-changed-users failed")
        assert r.ok

    @task(config.percentage('standalone_extension_locust'))
    @jira_measure("get-user-pull-status")
    def get_pull_status(self):
        user_key = 'admin'
        r = self.get(f'/rest/skillsforjira/1/user/updatedAfter?pull/status/{user_key}', catch_response=True)
        content = r.content.decode('utf-8')   # decode response content
    
        if not r.ok:
            logger.error(f"get-pull-status failed")
        assert r.ok
    
        enabled_pattern_example = '"enabled":"(.+?)"'
        enabled = re.findall(enabled_pattern_example, content)  # get TOKEN from response using regexp
    
        if 'enabled' not in content:
            logger.error(f"'enabled' was not found in {content}")
        assert 'enabled' in content  # assert specific string in response content

    @task(config.percentage('standalone_extension_locust'))
    @jira_measure("pull-task")
    def pull_task(self):
        body = {}  # include parsed variables to POST request body
        headers = {'content-type': 'application/json'}
        r = self.post('/rest/skillsforjira/1/assignments/pull', body, headers, catch_response=True)  # call app-specific POST endpoint
        content = r.content.decode('utf-8')
    
        if not r.ok:
            logger.error(f"pull-task failed")
        assert r.ok
    
        if 'enabled' not in content:
            logger.error(f"'enabled' was not found in {content}")
        assert 'enabled' in content  # assert specific string in response content


class BambooUser(HttpUser):
    host = BAMBOO_SETTINGS.server_url
    tasks = [BambooBehavior]
    wait_time = between(0, 0)

if __name__ == "__main__":
    run_single_user(BambooUser)