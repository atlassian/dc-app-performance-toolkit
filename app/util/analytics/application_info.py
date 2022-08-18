from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, BITBUCKET_SETTINGS, JSM_SETTINGS, CROWD_SETTINGS, \
    BAMBOO_SETTINGS
from util.api.jira_clients import JiraRestClient
from util.api.confluence_clients import ConfluenceRestClient
from util.api.bitbucket_clients import BitbucketRestClient
from util.api.crowd_clients import CrowdRestClient
from util.api.bamboo_clients import BambooClient
import json
from lxml import html

JIRA = 'jira'
CONFLUENCE = 'confluence'
BITBUCKET = 'bitbucket'
JSM = 'jsm'
CROWD = 'crowd'
BAMBOO = 'bamboo'
INSIGHT = 'insight'

DEFAULT_ACTIONS = 'util/default_test_actions.json'


def read_json_file(file_path):
    with open(file_path) as json_file:
        data = json.load(json_file)
        return data


class BaseApplication:
    type = None
    version = None
    nodes_count = None
    dataset_information = None

    def __init__(self, api_client, config_yml):
        self.client = api_client(host=config_yml.server_url,
                                 user=config_yml.admin_login, password=config_yml.admin_password)
        self.config = config_yml

    def get_default_actions(self):
        actions_json = read_json_file(DEFAULT_ACTIONS)
        return actions_json[self.type]

    @property
    def jmeter_default_actions(self):
        return self.get_default_actions()['jmeter']

    @property
    def selenium_default_actions(self):
        return self.get_default_actions()['selenium']

    @property
    def locust_default_actions(self):
        return self.get_default_actions()['locust']

    @property
    def processors(self):
        return self.client.get_available_processors()

    @property
    def deployment(self):
        return self.client.get_deployment_type()

    @property
    def java_version(self):
        return None  # TODO: Add Java version to results_summary.log for all supported products


class Jira(BaseApplication):
    type = JIRA

    @property
    def version(self):
        jira_server_info = self.client.get_server_info()
        jira_server_version = jira_server_info.get('version', '')
        return jira_server_version

    @property
    def nodes_count(self):
        return len(self.client.get_nodes())

    def __issues_count(self):
        return self.client.get_total_issues_count()

    @property
    def dataset_information(self):
        return f"{self.__issues_count()} issues"


class Confluence(BaseApplication):
    type = CONFLUENCE

    @property
    def version(self):
        return self.client.get_confluence_version()

    @property
    def nodes_count(self):
        return len(self.client.get_confluence_nodes())

    @property
    def dataset_information(self):
        return f"{self.client.get_total_pages_count()} pages"

    @property
    def java_version(self):
        full_system_info = self.client.get_system_info_page()
        java_versions_parsed = html.fromstring(full_system_info).xpath('//*[contains(@id, "java.version")]')
        if java_versions_parsed:
            return java_versions_parsed[0].text
        return None


class Bitbucket(BaseApplication):
    type = BITBUCKET

    @property
    def version(self):
        return self.client.get_bitbucket_version()

    @property
    def nodes_count(self):
        return self.client.get_bitbucket_nodes_count()

    @property
    def dataset_information(self):
        return f'{self.client.get_bitbucket_repo_count()} repositories'


class Jsm(BaseApplication):
    type = JSM

    @property
    def version(self):
        jsm_server_info = self.client.get_service_desk_info()
        return jsm_server_info.get('version', '')

    @property
    def nodes_count(self):
        return len(self.client.get_nodes())

    def __issues_count(self):
        return self.client.get_total_issues_count()

    @property
    def dataset_information(self):
        return f"{self.__issues_count()} issues"


class Crowd(BaseApplication):
    type = CROWD

    @property
    def version(self):
        crowd_server_info = self.client.get_server_info()
        return crowd_server_info.get('version', '')

    @property
    def nodes_count(self):
        cluster_nodes_info = self.client.get_cluster_nodes()
        nodes_count = len(cluster_nodes_info)
        return nodes_count if nodes_count > 0 else "server"

    def __users_count(self):
        self.application_crowd_client = CrowdRestClient(host=CROWD_SETTINGS.server_url,
                                                        user=CROWD_SETTINGS.application_name,
                                                        password=CROWD_SETTINGS.application_password)
        return len(self.application_crowd_client.search(start_index=0, max_results=-1, expand='user'))

    @property
    def dataset_information(self):
        return f"{self.__users_count()} users"


class Bamboo(BaseApplication):
    type = BAMBOO
    pass

    @property
    def version(self):
        server_info = self.client.get_server_info()
        return server_info['version']

    @property
    def nodes_count(self):
        return self.client.get_nodes_count()

    def __build_plans_count(self):
        return len(self.client.get_build_plans(max_result=2000))

    @property
    def dataset_information(self):
        return f"{self.__build_plans_count()} build plans"


class Insight(Jsm):
    type = INSIGHT


class ApplicationSelector:
    APP_TYPE_MSG = ('ERROR: Please run util/analytics.py with application type as argument. '
                    f'E.g. python util/analytics.py {JIRA}/{CONFLUENCE}/{BITBUCKET}/{JSM}/{BAMBOO}/{INSIGHT}')

    def __init__(self, app_name):
        self.application_type = self.__get_application_type(app_name)

    def __get_application_type(self, app_name):
        if app_name.lower() not in [JIRA, CONFLUENCE, BITBUCKET, JSM, CROWD, BAMBOO, INSIGHT]:
            raise SystemExit(self.APP_TYPE_MSG)
        return app_name.lower()

    @property
    def application(self):
        if self.application_type == JIRA:
            return Jira(api_client=JiraRestClient, config_yml=JIRA_SETTINGS)
        if self.application_type == CONFLUENCE:
            return Confluence(api_client=ConfluenceRestClient, config_yml=CONFLUENCE_SETTINGS)
        if self.application_type == BITBUCKET:
            return Bitbucket(api_client=BitbucketRestClient, config_yml=BITBUCKET_SETTINGS)
        if self.application_type == JSM:
            if JSM_SETTINGS.insight:
                return Insight(api_client=JiraRestClient, config_yml=JSM_SETTINGS)
            else:
                return Jsm(api_client=JiraRestClient, config_yml=JSM_SETTINGS)
        if self.application_type == CROWD:
            return Crowd(api_client=CrowdRestClient, config_yml=CROWD_SETTINGS)
        if self.application_type == BAMBOO:
            return Bamboo(api_client=BambooClient, config_yml=BAMBOO_SETTINGS)
