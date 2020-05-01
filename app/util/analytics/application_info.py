from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, BITBUCKET_SETTINGS
from api.jira_clients import JiraRestClient
from api.confluence_clients import ConfluenceRestClient
from api.bitbucket_clients import BitbucketRestClient
from lxml import etree

JIRA = 'jira'
CONFLUENCE = 'confluence'
BITBUCKET = 'bitbucket'


class BaseApplication:

    def __init__(self, api_client, config_yml):
        self.client = api_client(host=config_yml.server_url,
                                 user=config_yml.admin_login, password=config_yml.admin_password)
        self.config = config_yml


class Jira(BaseApplication):
    type = JIRA

    @property
    def version(self):
        jira_server_info = self.client.get_server_info()
        jira_server_version = jira_server_info.get('version', '')
        return jira_server_version

    @property
    def nodes_count(self):
        html_pattern = '<td><strong>Nodestate:</strong></td><td>Active</td>'
        if self.version >= '8.1.0':
            return len(self.client.get_nodes_info_via_rest())
        else:
            jira_system_page = self.client.get_system_info_page()
            node_count = jira_system_page.replace(' ', '').replace('\n', '').count(html_pattern)
            return node_count

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
        return len(self.client.get_confluence_nodes_count())

    @property
    def dataset_information(self):
        return f"{self.client.get_total_pages_count()} pages"


class Bitbucket(BaseApplication):
    type = BITBUCKET
    bitbucket_repos_selector = "#content-bitbucket\.atst\.repositories-0>.field-group>.field-value"

    @property
    def version(self):
        return self.client.get_bitbucket_version()

    @property
    def nodes_count(self):
        cluster_page = self.client.get_bitbucket_cluster_page()
        nodes_count = cluster_page.count('class="cluster-node-id" headers="cluster-node-id"')
        return nodes_count

    @property
    def dataset_information(self):
        system_page_html = self.client.get_bitbucket_system_page()
        dom = etree.HTML(system_page_html)
        repos_count = dom.cssselect(self.bitbucket_repos_selector)[0].text
        return f"{repos_count} repositories"


class ApplicationSelector:
    APP_TYPE_MSG = ('ERROR: Please run util/analytics.py with application type as argument. '
                    'E.g. python util/analytics.py jira')

    def __init__(self, *args):
        self.application_type = self.__get_application_type(args)

    def __get_application_type(self, args):
        try:
            app_type = args[0][1].lower()
            if app_type not in [JIRA, CONFLUENCE, BITBUCKET]:
                raise SystemExit(self.APP_TYPE_MSG)
            return app_type
        except IndexError:
            SystemExit(self.APP_TYPE_MSG)

    @property
    def application(self):
        if self.application_type == JIRA:
            return Jira(api_client=JiraRestClient, config_yml=JIRA_SETTINGS)
        if self.application_type == CONFLUENCE:
            return Confluence(api_client=ConfluenceRestClient, config_yml=CONFLUENCE_SETTINGS)
        if self.application_type == BITBUCKET:
            return Bitbucket(api_client=BitbucketRestClient, config_yml=BITBUCKET_SETTINGS)
