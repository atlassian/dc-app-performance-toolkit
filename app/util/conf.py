import yaml

from util.project_paths import JIRA_YML, CONFLUENCE_YML, BITBUCKET_YML, JSM_YML, CROWD_YML, BAMBOO_YML

TOOLKIT_VERSION = '8.11.0'
UNSUPPORTED_VERSION = '8.8.0'


def read_yml_file(file):
    with file.open(mode='r') as file:
        return yaml.load(file, Loader=yaml.FullLoader)


class BaseAppSettings:

    def __init__(self, config_yml):
        self.obj = read_yml_file(config_yml)
        self.settings = self.obj['settings']
        self.env_settings = self.obj['settings']['env']
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
        self.environment_compliance_check = self.get_property('environment_compliance_check')
        self.chromedriver_version = (
            self.obj.get('modules', {}).get('selenium', {}).get('chromedriver', {}).get('version', None))

    @property
    def server_url(self):
        return f'{self.protocol}://{self.hostname}:{self.port}{self.postfix}'

    @property
    def chrome_options(self):
        # Returns user-defined chrome options from the YML env section.
        # Supports 'arguments' (list) and 'experimental_options' (dict).
        options = self.env_settings.get('chrome_options') or {}
        return {
            'arguments': options.get('arguments') or [],
            'experimental_options': options.get('experimental_options') or {},
        }

    def get_property(self, property_name):
        if property_name not in self.env_settings:
            raise Exception(f'Application property {property_name} was not found in .yml configuration file')
        return self.env_settings[property_name]


class CustomizationInsightsSettings:

    def __init__(self, env_settings):
        config = env_settings.get('customization_insights') or {}
        self.ui_path = env_settings.get('customization_insights_ui_path') or config.get('ui_path') or ""
        self.ready_selector = env_settings.get('customization_insights_ready_selector') or config.get('ready_selector') or ""
        self.ready_selector_type = (
            env_settings.get('customization_insights_ready_selector_type') or config.get('ready_selector_type') or "css")
        self.detail_path = env_settings.get('customization_insights_detail_path') or config.get('detail_path') or ""
        self.detail_selector = env_settings.get('customization_insights_detail_selector') or config.get('detail_selector') or ""
        self.detail_selector_type = (
            env_settings.get('customization_insights_detail_selector_type') or config.get('detail_selector_type') or "css")
        self.rest_path = env_settings.get('customization_insights_rest_path') or config.get('rest_path') or ""
        self.rest_assertion = (
            env_settings.get('customization_insights_rest_assertion') or config.get('rest_assertion') or "")
        self.new_scan_selector = (
            env_settings.get('customization_insights_new_scan_selector') or config.get('new_scan_selector') or "")
        self.status_selector_type = (
            env_settings.get('customization_insights_status_selector_type') or config.get('status_selector_type') or "css")
        self.status_selector = env_settings.get('customization_insights_status_selector') or config.get('status_selector') or ""
        self.in_progress_text = (
            env_settings.get('customization_insights_in_progress_text') or config.get('in_progress_text') or "In progress")
        self.completed_text = (
            env_settings.get('customization_insights_completed_text') or config.get('completed_text') or "Done")
        self.scan_timeout = int(
            env_settings.get('customization_insights_scan_timeout') or config.get('scan_timeout') or 600)
        enabled = (env_settings['customization_insights_enabled']
                   if 'customization_insights_enabled' in env_settings
                   else config.get('enabled') or "false")
        self.enabled = str(enabled).lower() == "true"


class JiraSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.concurrency = self.get_property('concurrency')
        self.custom_dataset_query = self.get_property('custom_dataset_query') or ""
        self.verbose = self.settings['verbose']
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')
        self.local_chrome_binary_path = self.get_property('local_chrome_binary_path')
        self.customization_insights = CustomizationInsightsSettings(self.env_settings)


class ConfluenceSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.concurrency = self.get_property('concurrency')
        self.custom_dataset_query = self.get_property('custom_dataset_query') or ""
        self.verbose = self.settings['verbose']
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')
        self.extended_metrics = self.get_property('extended_metrics')
        self.local_chrome_binary_path = self.get_property('local_chrome_binary_path')
        self.customization_insights = CustomizationInsightsSettings(self.env_settings)


class BitbucketSettings(BaseAppSettings):

    def __init__(self, config_yml):
        super().__init__(config_yml)
        self.webdriver_visible = self.get_property('WEBDRIVER_VISIBLE')
        self.concurrency = self.get_property('concurrency')
        self.verbose = self.settings['verbose']
        self.total_actions_per_hour = self.get_property('total_actions_per_hour')
        self.local_chrome_binary_path = self.get_property('local_chrome_binary_path')


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
        self.local_chrome_binary_path = self.get_property('local_chrome_binary_path')


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
        self.local_chrome_binary_path = self.get_property('local_chrome_binary_path')


JIRA_SETTINGS = JiraSettings(config_yml=JIRA_YML)
CONFLUENCE_SETTINGS = ConfluenceSettings(config_yml=CONFLUENCE_YML)
BITBUCKET_SETTINGS = BitbucketSettings(config_yml=BITBUCKET_YML)
JSM_SETTINGS = JsmSettings(config_yml=JSM_YML)
CROWD_SETTINGS = CrowdSettings(config_yml=CROWD_YML)
BAMBOO_SETTINGS = BambooSettings(config_yml=BAMBOO_YML)
