import json

from locustio.common_utils import read_input_file, BaseResource
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


class JsmAgentsResource(BaseResource):

    def __init__(self, resource_file='locustio/jsm/agents/agents_resources.json'):
        super().__init__(resource_file)


class Login(JsmAgentsResource):
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


class AllOpenQueue(JsmAgentsResource):
    action_name = 'view_all_open_queue'
    last_visited_project_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-queues"}


class BrowseProjects(JsmAgentsResource):
    action_name = 'browse_jsm_projects'


class ViewRequest(JsmAgentsResource):
    action_name = 'view_request'


class AddComment(JsmAgentsResource):
    action_name = 'add_comment'


class ViewWorkloadReport(JsmAgentsResource):
    action_name = 'view_workload'
    last_visited_project_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-queues"}


class ViewTimeToResolutionReport(JsmAgentsResource):
    action_name = 'view_time_to_resolution'
    last_visited_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-reports"}


class ViewReportCreatedVsResolved(JsmAgentsResource):
    action_name = 'view_created_vs_resolved'
    last_visited_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-reports"}


class ViewCustomers(JsmAgentsResource):
    action_name = 'view_customers'
    last_visited_body = {"id": "com.atlassian.servicedesk.project-ui:sd-project-sidebar-customers"}
