import yaml

from util.project_paths import JIRA_YML, CONFLUENCE_YML, BITBUCKET_YML, JSM_YML, CROWD_YML, BAMBOO_YML

TOOLKIT_VERSION = '7.2.0'
UNSUPPORTED_VERSION = '6.0.0'


def read_yml_file(file):
    with file.open(mode='r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


class BaseAppSettings:

    def __init__(self, config_yml):
        obj = read_yml_file(config_yml)
        self.settings = obj['settings']
        self.env_settings = obj['settings']['env']
        self.hostname = self.get_property('application_hostname')
        self.protocol = self.get_property('application_protocol')
        self.port = self.get_property('application_port')
        self.postfix = self.get_property('application_postfix') or ""
        self.admin_login = self.get_property('admin_login')
        self.admin_password = self.get_property('admin_password')
        self.duration = self.get_property('test_duration')
        self.analytics_collector = self.get_property('allow_analytics')
        self.load_executor = self.get_property('load_executor')
        self.secure = self.get_property('secure')

    @property
    def server_url(self):
        return f'{self.protocol}://{self.hostname}:{self.port}{self.postfix}'

    def get_property(self, property_name):
        if property_name not in self.env_settings:
            raise Exception(f'Application property {property_name} was not found in .yml configuration file')
        return self.env_settings[property_name]


class JiraSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.concurrency = self.get_property('concurrency')
        self.custom_dataset_query = self.get_property('custom_dataset_query') or ""
        self.verbose = self.settings['verbose']
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')


class ConfluenceSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.concurrency = self.get_property('concurrency')
        self.custom_dataset_query = self.get_property('custom_dataset_query') or ""
        self.verbose = self.settings['verbose']
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')
        self.extended_metrics = self.get_property('extended_metrics')


class BitbucketSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.concurrency = self.get_property('concurrency')
        self.verbose = self.settings['verbose']
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')


class JsmSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.agents_concurrency = self.get_property('concurrency_agents')
        self.agents_total_actions_per_hr = self.get_property('total_actions_per_hour_agents')
        self.customers_total_actions_per_hr = self.get_property('total_actions_per_hour_customers')
        self.customers_concurrency = self.env_settings['concurrency_customers']
        self.concurrency = self.agents_concurrency + self.customers_concurrency
        self.custom_dataset_query = self.get_property('custom_dataset_query') or ""
        self.verbose = self.settings['verbose']
        self.insight = self.get_property('insight')


class CrowdSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.concurrency = self.get_property('concurrency')
        self.application_name = self.get_property('application_name')
        self.application_password = self.get_property('application_password')
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')
        self.ramp_up = self.get_property('ramp-up')


class BambooSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.concurrency = self.get_property('concurrency')
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.verbose = self.settings['verbose']
        self.number_of_agents = self.env_settings['number_of_agents']
        self.parallel_plans_count = self.env_settings['parallel_plans_count']
        self.start_plan_timeout = self.env_settings['start_plan_timeout']
        self.default_dataset_plan_duration = self.env_settings['default_dataset_plan_duration']
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')


JIRA_SETTINGS = JiraSettings(config_yml=JIRA_YML)
CONFLUENCE_SETTINGS = ConfluenceSettings(config_yml=CONFLUENCE_YML)
BITBUCKET_SETTINGS = BitbucketSettings(config_yml=BITBUCKET_YML)
JSM_SETTINGS = JsmSettings(config_yml=JSM_YML)
CROWD_SETTINGS = CrowdSettings(config_yml=CROWD_YML)
BAMBOO_SETTINGS = BambooSettings(config_yml=BAMBOO_YML)
