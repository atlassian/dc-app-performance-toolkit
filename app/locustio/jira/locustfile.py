from locust import HttpLocust, TaskSet, task, between
from locustio.jira.http_actions import login_and_view_dashboard, create_issue, search_jql, view_issue, \
    view_project_summary, view_dashboard, edit_issue, add_comment, browse_boards, view_kanban_board, view_scrum_board, \
    view_backlog, browse_projects
from locustio.common_utils import ActionPercentage
from extension.jira.extension_locust import custom_action
from util.conf import JIRA_SETTINGS

action = ActionPercentage(config_yml=JIRA_SETTINGS)


class JiraBehavior(TaskSet):

    def on_start(self):
        login_and_view_dashboard(self)

    @task(action.percentage('create_issue'))
    def create_issue(self):
        create_issue(self)

    @task(action.percentage('search_jql'))
    def search_jql(self):
        search_jql(self)

    @task(action.percentage('view_issue'))
    def view_issue(self):
        view_issue(self)

    @task(action.percentage('view_project_summary'))
    def view_project_summary(self):
        view_project_summary(self)

    @task(action.percentage('view_dashboard'))
    def view_dashboard(self):
        view_dashboard(self)

    @task(action.percentage('edit_issue'))
    def edit_issue(self):
        edit_issue(self)

    @task(action.percentage('add_comment'))
    def add_comment(self):
        add_comment(self)

    @task(action.percentage('browse_projects'))
    def browse_projects(self):
        browse_projects(self)

    @task(action.percentage('view_kanban_board'))
    def view_kanban_board(self):
        view_kanban_board(self)

    @task(action.percentage('view_scrum_board'))
    def view_scrum_board(self):
        view_scrum_board(self)

    @task(action.percentage('view_backlog'))
    def view_backlog(self):
        view_backlog(self)

    @task(action.percentage('browse_boards'))
    def browse_boards(self):
        browse_boards(self)

    @task(action.percentage('standalone_extension'))  # By default disabled
    def custom_action(self):
        custom_action(self)


class JiraUser(HttpLocust):
    host = JIRA_SETTINGS.server_url
    task_set = JiraBehavior
    wait_time = between(0, 0)
