from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, BITBUCKET_SETTINGS, JSM_SETTINGS
from util.api.jira_clients import JiraRestClient
from util.api.confluence_clients import ConfluenceRestClient
from util.api.bitbucket_clients import BitbucketRestClient
from lxml import etree

JIRA = 'jira'
CONFLUENCE = 'confluence'
BITBUCKET = 'bitbucket'
JSM = 'jsm'


class BaseApplication:
    type = None
    version = None
    nodes_count = None
    dataset_information = None

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
        return self.client.get_cluster_nodes_count(jira_version=self.version)

    def __issues_count(self):
        return self.client.get_total_issues_count()

    @property
    def dataset_information(self):
        return f"{self.__issues_count()} issues"

    @property
    def jmeter_default_actions(self):
        return ['jmeter_create_issue:open_quick_create',
                'jmeter_create_issue:fill_and_submit_issue_form',
                'jmeter_search_jql',
                'jmeter_view_issue',
                'jmeter_view_project_summary',
                'jmeter_view_dashboard',
                'jmeter_edit_issue:open_editor',
                'jmeter_edit_issue:save_edit',
                'jmeter_add_comment:open_comment',
                'jmeter_add_comment:save_comment',
                'jmeter_browse_projects',
                'jmeter_view_kanban_board',
                'jmeter_view_scrum_board',
                'jmeter_view_backlog',
                'jmeter_browse_boards',
                'jmeter_login_and_view_dashboard',
                ]

    @property
    def selenium_default_actions(self):
        return ['selenium_a_login',
                'selenium_browse_projects_list',
                'selenium_browse_boards_list',
                'selenium_create_issue',
                'selenium_edit_issue',
                'selenium_save_comment',
                'selenium_search_jql',
                'selenium_view_backlog_for_scrum_board',
                'selenium_view_scrum_board',
                'selenium_view_kanban_board',
                'selenium_view_dashboard',
                'selenium_view_issue',
                'selenium_view_project_summary',
                'selenium_z_log_out',
                ]

    @property
    def locust_default_actions(self):
        return ['locust_login_and_view_dashboard',
                'locust_view_issue',
                'locust_create_issue:open_quick_create',
                'locust_create_issue:fill_and_submit_issue_form',
                'locust_search_jql',
                'locust_view_project_summary',
                'locust_edit_issue:open_editor',
                'locust_edit_issue:save_edit',
                'locust_view_dashboard',
                'locust_add_comment:open_comment',
                'locust_add_comment:save_comment',
                'locust_browse_projects',
                'locust_view_kanban_board',
                'locust_view_scrum_board',
                'locust_view_backlog',
                'locust_browse_boards',
                ]


class Confluence(BaseApplication):
    type = CONFLUENCE

    @property
    def version(self):
        return self.client.get_confluence_version()

    @property
    def nodes_count(self):
        return self.client.get_confluence_nodes_count()

    @property
    def dataset_information(self):
        return f"{self.client.get_total_pages_count()} pages"

    @property
    def jmeter_default_actions(self):
        return ['jmeter_login_and_view_dashboard',
                'jmeter_view_page:open_page',
                'jmeter_view_page:view_page_tree',
                'jmeter_view_dashboard',
                'jmeter_view_blog',
                'jmeter_search_cql:recently_viewed',
                'jmeter_search_cql:search_results',
                'jmeter_view_blog',
                'jmeter_search_cql:recently_viewed',
                'jmeter_search_cql:search_results',
                'jmeter_create_blog:blog_editor',
                'jmeter_create_blog:feel_and_publish',
                'jmeter_create_and_edit_page:create_page_editor',
                'jmeter_create_and_edit_page:create_page',
                'jmeter_create_and_edit_page:open_editor',
                'jmeter_create_and_edit_page:edit_page',
                'jmeter_comment_page',
                'jmeter_view_attachment',
                'jmeter_upload_attachment',
                'jmeter_like_page'
                ]

    @property
    def selenium_default_actions(self):
        return ['selenium_a_login',
                'selenium_create_comment',
                'selenium_create_page',
                'selenium_edit_page',
                'selenium_view_blog',
                'selenium_view_dashboard',
                'selenium_view_page',
                'selenium_z_log_out',
                ]

    @property
    def locust_default_actions(self):
        return ['locust_login_and_view_dashboard',
                'locust_view_page:open_page',
                'locust_view_page:view_page_tree',
                'locust_view_dashboard',
                'locust_view_blog',
                'locust_search_cql:recently_viewed',
                'locust_search_cql:search_results',
                'locust_create_blog:blog_editor',
                'locust_create_blog:feel_and_publish',
                'locust_create_and_edit_page:create_page_editor',
                'locust_create_and_edit_page:create_page',
                'locust_create_and_edit_page:open_editor',
                'locust_create_and_edit_page:edit_page',
                'locust_comment_page',
                'locust_view_attachment',
                'locust_upload_attachment',
                'locust_like_page',
                ]


class Bitbucket(BaseApplication):
    type = BITBUCKET
    bitbucket_repos_selector = "#content-bitbucket\.atst\.repositories-0>.field-group>.field-value"  # noqa W605

    @property
    def version(self):
        return self.client.get_bitbucket_version()

    @property
    def nodes_count(self):
        return self.client.get_bitbucket_nodes_count()

    @property
    def dataset_information(self):
        system_page_html = self.client.get_bitbucket_system_page()
        if 'Repositories' in system_page_html:
            dom = etree.HTML(system_page_html)
            repos_count = dom.cssselect(self.bitbucket_repos_selector)[0].text
            return f'{repos_count} repositories'
        else:
            return 'Could not parse number of Bitbucket repositories'

    @property
    def jmeter_default_actions(self):
        return ['jmeter_clone_repo_via_http',
                'jmeter_clone_repo_via_ssh',
                'jmeter_create_repo_shallow_copy',
                'jmeter_git_add',
                'jmeter_git_commit',
                'jmeter_git_push_via_http',
                'jmeter_git_push_via_ssh',
                'jmeter_git_fetch_via_http',
                'jmeter_git_fetch_via_ssh',
                ]

    @property
    def selenium_default_actions(self):
        return ['selenium_a_login',
                'selenium_view_dashboard',
                'selenium_create_pull_request',
                'selenium_view_projects',
                'selenium_view_project_repositories',
                'selenium_view_repo',
                'selenium_view_list_pull_requests',
                'selenium_view_pull_request_overview',
                'selenium_view_pull_request_diff',
                'selenium_view_pull_request_commits',
                'selenium_comment_pull_request_diff',
                'selenium_comment_pull_request_overview',
                'selenium_view_branches',
                'selenium_view_commits',
                'selenium_logout',
                ]


class Jsm(BaseApplication):
    type = JSM

    @property
    def version(self):
        jsm_server_info = self.client.get_service_desk_info()
        return jsm_server_info.get('version', '')

    @property
    def nodes_count(self):
        jira_server_info = self.client.get_server_info()
        jira_server_version = jira_server_info.get('version', '')
        return self.client.get_cluster_nodes_count(jira_version=jira_server_version)

    def __issues_count(self):
        return self.client.get_total_issues_count()

    @property
    def dataset_information(self):
        return f"{self.__issues_count()} issues"

    @property
    def jmeter_default_actions(self):
        return ['jmeter_agent_add_comment:open_request_comment',
                'jmeter_agent_add_comment:save_request_comment',
                'jmeter_agent_browse_projects',
                'jmeter_agent_login_and_view_dashboard',
                'jmeter_agent_view_customers',
                'jmeter_agent_view_queues_medium:all_open_queue',
                'jmeter_agent_view_queues_medium:random_queue',
                'jmeter_agent_view_queues_small:all_open_queue',
                'jmeter_agent_view_queues_small:random_queue',
                'jmeter_agent_view_report_created_vs_resolved_medium',
                'jmeter_agent_view_report_created_vs_resolved_small',
                'jmeter_agent_view_report_workload_medium',
                'jmeter_agent_view_report_workload_small',
                'jmeter_agent_view_request',
                'jmeter_customer_add_comment',
                'jmeter_customer_create_request:create_request',
                'jmeter_customer_create_request:open_create_request_view',
                'jmeter_customer_create_request:view_request_after_creation',
                'jmeter_customer_login_and_view_portals',
                'jmeter_customer_share_request_with_customer:add_customer',
                'jmeter_customer_share_request_with_customer:remove_customer',
                'jmeter_customer_share_request_with_customer:search_customer',
                'jmeter_customer_share_request_with_org:add_org',
                'jmeter_customer_share_request_with_org:remove_org',
                'jmeter_customer_share_request_with_org:search_org',
                'jmeter_customer_view_portal',
                'jmeter_customer_view_request',
                'jmeter_customer_view_requests:all_requests',
                'jmeter_customer_view_requests:my_requests',
                'jmeter_customer_view_requests:with_filter_requests']

    @property
    def selenium_default_actions(self):
        return ['selenium_agent_a_login',
                'selenium_agent_add_comment',
                'selenium_agent_browse_projects',
                'selenium_agent_view_customers',
                'selenium_agent_view_queues_medium',
                'selenium_agent_view_queues_small',
                'selenium_agent_view_report_created_vs_resolved_medium',
                'selenium_agent_view_report_created_vs_resolved_small',
                'selenium_agent_view_report_workload_medium',
                'selenium_agent_view_report_workload_small',
                'selenium_agent_view_request',
                'selenium_agent_z_logout',
                'selenium_customer_a_login',
                'selenium_customer_add_comment',
                'selenium_customer_create_request',
                'selenium_customer_share_request_with_customer',
                'selenium_customer_view_all_requests',
                'selenium_customer_view_request',
                'selenium_customer_view_requests',
                'selenium_customer_z_log_out']

    @property
    def locust_default_actions(self):
        return ['locust_agent_add_comment:open_request_comment',
                'locust_agent_add_comment:save_request_comment',
                'locust_agent_browse_projects',
                'locust_agent_login_and_view_dashboard',
                'locust_agent_view_customers',
                'locust_agent_view_queues_medium:all_open_queue',
                'locust_agent_view_queues_medium:random_queue',
                'locust_agent_view_queues_small:all_open_queue',
                'locust_agent_view_queues_small:random_queue',
                'locust_agent_view_report_created_vs_resolved_medium',
                'locust_agent_view_report_created_vs_resolved_small',
                'locust_agent_view_report_workload_medium',
                'locust_agent_view_report_workload_small',
                'locust_agent_view_request',
                'locust_customer_add_comment',
                'locust_customer_create_request:create_request',
                'locust_customer_create_request:open_create_request_view',
                'locust_customer_create_request:view_request_after_creation',
                'locust_customer_login_and_view_portals',
                'locust_customer_share_request_with_customer:add_customer',
                'locust_customer_share_request_with_customer:remove_customer',
                'locust_customer_share_request_with_customer:search_customer',
                'locust_customer_share_request_with_org:add_org',
                'locust_customer_share_request_with_org:remove_org',
                'locust_customer_share_request_with_org:search_org',
                'locust_customer_view_portal',
                'locust_customer_view_request',
                'locust_customer_view_requests:all_requests',
                'locust_customer_view_requests:my_requests',
                'locust_customer_view_requests:with_filter_requests']


class ApplicationSelector:
    APP_TYPE_MSG = ('ERROR: Please run util/analytics.py with application type as argument. '
                    'E.g. python util/analytics.py jira/confluence/bitbucket/jsm')

    def __init__(self, app_name):
        self.application_type = self.__get_application_type(app_name)

    def __get_application_type(self, app_name):
        if app_name.lower() not in [JIRA, CONFLUENCE, BITBUCKET, JSM]:
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
            return Jsm(api_client=JiraRestClient, config_yml=JSM_SETTINGS)
