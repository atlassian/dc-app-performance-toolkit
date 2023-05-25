import re
import time

from locust import HttpUser, task, between, run_single_user
from locustio.jira.http_actions import login_and_view_dashboard, create_issue, search_jql, view_issue, \
    view_project_summary, view_dashboard, edit_issue, add_comment, browse_boards, view_kanban_board, view_scrum_board, \
    view_backlog, browse_projects
from locustio.common_utils import LocustConfig, MyBaseTaskSet, init_logger, jira_measure, run_as_specific_user  # noqa F401
from util.conf import JIRA_SETTINGS

config = LocustConfig(config_yml=JIRA_SETTINGS)
logger = init_logger(app_type='jira')
startedAt = round(time.time())

class SkillsForJiraBehavior(MyBaseTaskSet):
    def on_start(self):
        self.client.verify = config.secure
        login_and_view_dashboard(self)

    @task(config.percentage('standalone_extension'))
    @jira_measure("get-users")
    @run_as_specific_user(username='admin', password='admin')  # run as specific user
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

    @task(config.percentage('standalone_extension'))
    @run_as_specific_user(username='admin', password='admin')  # run as specific user
    @jira_measure("get-changed-users")
    def get_changed_users(self):
        r = self.get(f'/rest/skillsforjira/1/user/updatedAfter?timestamp={startedAt}', catch_response=False)  # call app-specific GET endpoint
        assert r.ok

    @task(config.percentage('standalone_extension'))
    @run_as_specific_user(username='admin', password='admin')  # run as specific user
    @jira_measure("get-user-pull-status")
    def get_pull_status(self):
        r = self.get(f'/rest/skillsforjira/1/assignments/pull/status/{self.session_data_storage["username"]}', catch_response=True)
        content = r.content.decode('utf-8')   # decode response content
    
        if not r.ok:
            logger.error(f"get-pull-status failed")
        assert r.ok
    
        enabled_pattern_example = '"enabled":"(.+?)"'
        enabled = re.findall(enabled_pattern_example, content)  # get TOKEN from response using regexp
    
        if 'enabled' not in content:
            logger.error(f"'enabled' was not found in {content}")
        assert 'enabled' in content  # assert specific string in response content

    @task(config.percentage('standalone_extension'))
    @run_as_specific_user(username='admin', password='admin')  # run as specific user
    @jira_measure("pull-task")
    def pull_task(self):
        body = {}  # include parsed variables to POST request body
        headers = {'content-type': 'application/json'}
        r = self.post(f'/rest/skillsforjira/1/assignments/pull/admin', json=body, headers=headers, catch_response=True)  # call app-specific POST endpoint
        content = r.content.decode('utf-8')
    
        if 'enabled' not in content:
            logger.error(f"'enabled' was not found in {content}")
        assert 'enabled' in content  # assert specific string in response content


    @jira_measure("run_risk_analysis_page")
    @task(config.percentage('standalone_extension'))
    @run_as_specific_user(username='admin', password='admin')  # run as specific user
    def run_risk_analysis_page(self):
        body = {
            "jql": "type=Task",
            "userKeys": [ self.session_data_storage["username"] ],
            "groupNames": [],
        } 
        headers = {'content-type': 'application/json'}
        r = self.post(f'/rest/skillsforjira/1/risks', json=body, headers=headers, catch_response=True)  # call app-specific POST endpoint
        content = r.content.decode('utf-8')

        if 'issuesAtRisk' not in content:
            logger.error(f"'issuesAtRisk' was not found in {content}")
        assert 'issuesAtRisk' in content  # assert specific string in response content
        
    @jira_measure("run_simulation_page")
    @task(config.percentage('standalone_extension'))
    @run_as_specific_user(username='admin', password='admin')  # run as specific user
    def run_simulation(self):
        body = {
            "userKeys": [ self.session_data_storage["username"] ],
            "groupNames": [],
            "queueIds": [],
            "simulationEndAt": startedAt + 1000 * 5,
            "batchDescriptor": None
        }
        headers = {'content-type': 'application/json'}
        r = self.post(f'/rest/skillsforjira/1/simulation', json=body, headers=headers, catch_response=True)  # call app-specific POST endpoint
        content = r.content.decode('utf-8')

        if 'pulls' not in content:
            logger.error(f"'pulls' was not found in {content}")
        assert 'pulls' in content  # assert specific string in response content
    
    @jira_measure("get_skilltree")
    @task(config.percentage('standalone_extension'))
    def get_skilltree(self):
        r = self.get(f'/rest/skillsforjira/1/skilltree/global', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'nodes' in content
        
    @jira_measure("get_all_expertise")
    @task(config.percentage('standalone_extension'))
    def get_all_expertise(self):
        r = self.get(f'/rest/skillsforjira/1/expertise', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'skillsByUserKey' in content
    
    @jira_measure("get_user_expertise")
    @task(config.percentage('standalone_extension'))
    def get_user_expertise(self):
        r = self.get(f'/rest/skillsforjira/1/expertise/admin', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert content.startswith('[')

    
class SkillsForJiraUser(HttpUser):
    host = JIRA_SETTINGS.server_url
    tasks = [SkillsForJiraBehavior]
    wait_time = between(0, 0)

if __name__ == "__main__":
    run_single_user(SkillsForJiraUser)
