from locust import HttpUser, task, between
from locustio.jsm.agents import agents_http_actions
from locustio.common_utils import LocustConfig, MyBaseTaskSet
from locustio.jsm.agents.agents_requests_params import jsm_agent_datasets
from extension.jsm.extension_locust_agents import app_specific_action
from util.conf import JSM_SETTINGS


config = LocustConfig(config_yml=JSM_SETTINGS)
jsm_agent_dataset = jsm_agent_datasets()


class JsmAgentBehavior(MyBaseTaskSet):

    def on_start(self):
        self.client.verify = config.secure
        agents_http_actions.agent_login_and_view_dashboard(self, jsm_agent_dataset)

    @task(config.percentage('agent_view_queues_small'))
    def agent_small_view_queue_all_open(self):
        agents_http_actions.agent_small_view_queue_all_open(self)
        agents_http_actions.agent_small_view_queue_random(self)

    @task(config.percentage('agent_view_queues_medium'))
    def agent_medium_view_queue_all_open(self):
        if jsm_agent_dataset['m_project']:
            agents_http_actions.agent_medium_view_queue_all_open(self)
            agents_http_actions.agent_medium_view_queue_random(self)

    @task(config.percentage('agent_browse_projects'))
    def agent_browse_projects(self):
        agents_http_actions.agent_browse_jsm_projects(self)

    @task(config.percentage('agent_view_request'))
    def agent_view_service_desk_request(self):
        agents_http_actions.agent_view_service_desk_request(self)

    @task(config.percentage('agent_add_comment'))
    def agent_add_comment(self):
        agents_http_actions.agent_add_comment(self)

    @task(config.percentage('agent_view_report_workload_small'))
    def agent_view_workload_report_small(self):
        agents_http_actions.agent_small_view_workload_report(self)

    @task(config.percentage('agent_view_report_workload_medium'))
    def agent_view_workload_report_medium(self):
        if jsm_agent_dataset['m_project']:
            agents_http_actions.agent_medium_view_workload_report(self)

    @task(config.percentage('agent_view_report_time_to_resolution_small'))
    def agent_view_time_to_resolution_report_small(self):
        agents_http_actions.agent_small_view_time_to_resolution_report(self)

    @task(config.percentage('agent_view_report_time_to_resolution_medium'))
    def agent_view_time_to_resolution_report_medium(self):
        if jsm_agent_dataset['m_project']:
            agents_http_actions.agent_medium_view_time_to_resolution_report(self)

    @task(config.percentage('agent_view_report_created_vs_resolved_small'))
    def agent_view_created_vs_resolved_report_small(self):
        agents_http_actions.agent_small_view_created_vs_resolved_report(self)

    @task(config.percentage('agent_view_report_created_vs_resolved_medium'))
    def agent_view_created_vs_resolved_report_medium(self):
        if jsm_agent_dataset['m_project']:
            agents_http_actions.agent_medium_view_created_vs_resolved_report(self)

    @task(config.percentage('agent_view_customers'))
    def agent_view_customers(self):
        agents_http_actions.agent_view_customers(self)

    @task(config.percentage('standalone_extension'))  # By default disabled
    def custom_action(self):
        app_specific_action(self)


class JsmAgent(HttpUser):
    host = JSM_SETTINGS.server_url
    tasks = [JsmAgentBehavior]
    wait_time = between(0, 0)
