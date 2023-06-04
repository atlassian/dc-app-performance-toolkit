import re
import time
import urllib

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

    @jira_measure("locust_sfj_get_servlet_config")
    @task(config.percentage('sfj_get_servlet_config'))
    def get_servlet_config(self):
        r = self.get(f'/plugins/servlet/skillsforjira/config')
        assert r.ok

    @jira_measure("locust_sfj_get_servlet_team")
    @task(config.percentage('sfj_get_servlet_team'))
    def get_servlet_team(self):
        r = self.get(f'/plugins/servlet/skillsforjira/team')
        assert r.ok

    @jira_measure("locust_sfj_get-users")
    @task(config.percentage('sfj_get_users'))
    def get_users(self):
        r = self.get('/rest/skillsforjira/1/user', catch_response=True)  # call app-specific GET endpoint
        content = r.content.decode('utf-8')   # decode response content
        assert r.ok
        assert 'key' in content  # assert specific string in response content

    @jira_measure("locust_sfj_get-changed-users")
    @task(config.percentage('sfj_get_changed_users'))
    def get_changed_users(self):
        r = self.get(f'/rest/skillsforjira/1/user/updatedAfter?timestamp={startedAt}', catch_response=False)  # call app-specific GET endpoint
        assert r.ok

    @jira_measure("locust_sfj_get-user-pull-status")
    @task(config.percentage('sfj_get_pull_status'))
    def get_pull_status(self):
        r = self.get(f'/rest/skillsforjira/1/assignments/pull/status/{self.session_data_storage["username"]}', catch_response=True)
        content = r.content.decode('utf-8')   # decode response content
    
        assert r.ok
        assert 'enabled' in content  # assert specific string in response content

    # NOTE: We don't have current user key with locust. And users can't pull on behalf of other users.
    # @jira_measure("locust_sfj_pull-task")
    # @task(config.percentage('sfj_pull_task'))
    # def pull_task(self):
    #     body = {}  # include parsed variables to POST request body
    #     headers = {'content-type': 'application/json'}
    #     r = self.post(f'/rest/skillsforjira/1/assignments/pull/admin', json=body, headers=headers, catch_response=True)  # call app-specific POST endpoint
    #     content = r.content.decode('utf-8')
    # 
    #     assert r.ok
    #     assert 'enabled' in content  # assert specific string in response content


    @jira_measure("locust_sfj_run_risk_analysis_page")
    @task(config.percentage('sfj_run_risk_analysis_page'))
    def run_risk_analysis_page(self):
        body = {
            "jql": "type=Task",
            "userKeys": [ self.session_data_storage["username"] ],
            "groupNames": [],
        } 
        headers = {'content-type': 'application/json'}
        r = self.post(f'/rest/skillsforjira/1/risks', json=body, headers=headers, catch_response=True)  # call app-specific POST endpoint
        content = r.content.decode('utf-8')

        assert r.ok   
        assert 'issuesAtRisk' in content  # assert specific string in response content
        
    @jira_measure("locust_sfj_run_simulation_page")
    @task(config.percentage('sfj_run_simulation_page'))
    def run_simulation_page(self):
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

        assert r.ok
        assert 'pulls' in content  # assert specific string in response content
    
    @jira_measure("locust_sfj_get_skilltree")
    @task(config.percentage('sfj_get_skilltree'))
    def get_skilltree(self):
        r = self.get(f'/rest/skillsforjira/1/skilltree/global', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'nodes' in content
        
    @jira_measure("locust_sfj_get_all_expertise")
    @task(config.percentage('sfj_get_all_expertise'))
    def get_all_expertise(self):
        r = self.get(f'/rest/skillsforjira/1/expertise', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'skillsByUserKey' in content
        
    @jira_measure("locust_sfj_get_expertise_coverage")
    @task(config.percentage('sfj_get_expertise_coverage'))
    def get_expertise_coverage(self):
        jql = "project = aaeneus"
        r = self.get(f'/rest/skillsforjira/1/expertise/coverage/admin?jql={urllib.parse.quote(jql)}', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'demandInfoBySkillsetKey' in content
    
    @jira_measure("locust_sfj_get_user_expertise")
    @task(config.percentage('sfj_get_user_expertise'))
    def get_user_expertise(self):
        r = self.get(f'/rest/skillsforjira/1/expertise/admin', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert content.startswith('[')
        
    @jira_measure("locust_sfj_get_queues")
    @task(config.percentage('sfj_get_queues'))
    def get_queues(self):
        r = self.get(f'/rest/skillsforjira/1/queue', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert content.startswith('[')
        
    @jira_measure("locust_sfj_get_user_queues")
    @task(config.percentage('sfj_get_user_queues'))
    def get_user_queues(self):
        r = self.get(f'/rest/skillsforjira/1/queue/user/admin', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert content.startswith('[')
        
    @jira_measure("locust_sfj_validate_queues")
    @task(config.percentage('sfj_valiate_queues'))
    def valiate_queues(self):
        r = self.get(f'/rest/skillsforjira/1/queue/validate', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'ok' in content
        
    @jira_measure("locust_sfj_get_analytics_config")
    @task(config.percentage('sfj_get_analytics_config'))
    def get_analytics_config(self):
        r = self.get(f'/rest/skillsforjira/1/config/analytics', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'isEnabled' in content
        
    @jira_measure("locust_sfj_get_assignments_config")
    @task(config.percentage('sfj_get_assignments_config'))
    def get_assignments_config(self):
        r = self.get(f'/rest/skillsforjira/1/config/assignments', catch_response=False)
        content = r.content.decode('utf-8')
        assert r.ok
        assert 'mode' in content

    
class SkillsForJiraUser(HttpUser):
    host = JIRA_SETTINGS.server_url
    tasks = [SkillsForJiraBehavior]
    wait_time = between(0, 0)

if __name__ == "__main__":
    run_single_user(SkillsForJiraUser)
