import json

from locustio.common_utils import read_input_file
from util.project_paths import JSM_DATASET_AGENTS, JSM_DATASET_REQUESTS, JSM_DATASET_SERVICE_DESKS_L, \
    JSM_DATASET_SERVICE_DESKS_M, JSM_DATASET_SERVICE_DESKS_S


def jsm_agent_datasets():
    data_sets = dict()
    data_sets['agents'] = read_input_file(JSM_DATASET_AGENTS)
    data_sets['requests'] = read_input_file(JSM_DATASET_REQUESTS)
    data_sets['s_project'] = read_input_file(JSM_DATASET_SERVICE_DESKS_S)
    data_sets['m_project'] = read_input_file(JSM_DATASET_SERVICE_DESKS_M)
    data_sets['l_project'] = read_input_file(JSM_DATASET_SERVICE_DESKS_L)

    return data_sets


class BaseResource:
    resources_file = 'locustio/jsm/agents/agents_resources.json'
    action_name = ''

    def __init__(self):
        self.resources_json = self.read_json()
        self.resources_body = self.action_resources()

    def read_json(self):
        with open(self.resources_file, encoding='UTF-8') as f:
            return json.load(f)

    def action_resources(self):
        return self.resources_json[self.action_name] if self.action_name in self.resources_json else dict()


class Login(BaseResource):
    action_name = 'login_and_view_dashboard'
    atl_token_pattern = r'name="atlassian-token" content="(.+?)">'
    login_body = {
        'os_username': '',
        'os_password': '',
        'os_destination': '',
        'user_role': '',
        'atl_token': '',
        'login': 'Log in'
    }


class AllOpenQueue(BaseResource):
    action_name = 'view_all_open_queue'
    last_visited_project_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-queues"}


class BrowseProjects(BaseResource):
    action_name = 'browse_jsm_projects'


class ViewRequest(BaseResource):
    action_name = 'view_request'


class AddComment(BaseResource):
    action_name = 'add_comment'


class ViewWorkloadReport(BaseResource):
    action_name = 'view_workload'
    last_visited_project_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-queues"}


class ViewTimeToResolutionReport(BaseResource):
    action_name = 'view_time_to_resolution'
    last_visited_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-reports"}


class ViewReportCreatedVsResolved(BaseResource):
    action_name = 'view_created_vs_resolved'
    last_visited_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-reports"}


class ViewCustomers(BaseResource):
    action_name = 'view_customers'
    last_visited_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-customers"}
