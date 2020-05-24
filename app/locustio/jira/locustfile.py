from locust import HttpLocust, TaskSet, task, between
from locustio.jira.http_actions import login_and_view_dashboard, create_issue, search_jql, view_issue, \
    view_project_summary, view_dashboard, edit_issue, add_comment, browse_boards, view_kanban_board, view_scrum_board, \
    view_backlog, browse_projects
from locustio.common_utils import init_logger
from util.conf import JIRA_SETTINGS

init_logger()


class JiraBehavior(TaskSet):

    def on_start(self):
        login_and_view_dashboard(self)

    @task(2)
    def create_issue(self):
        create_issue(self)

    @task(6)
    def search_jql(self):
        search_jql(self)

    @task(20)
    def view_issue(self):
        view_issue(self)

    @task(3)
    def view_project_sumamry(self):
        view_project_summary(self)

    @task(6)
    def view_dashboard(self):
        view_dashboard(self)

    @task(2)
    def edit_issue(self):
        edit_issue(self)

    @task(1)
    def add_comment(self):
        add_comment(self)

    @task(2)
    def browse_projects(self):
        browse_projects(self)

    @task(2)
    def view_kanban_board(self):
        view_kanban_board(self)

    @task(2)
    def view_scrum_board(self):
        view_scrum_board(self)

    @task(3)
    def view_backlog(self):
        view_backlog(self)

    @task(1)
    def browse_boards(self):
        browse_boards(self)

    # @task(1)
    # def custom_action(self):
    #     custom_action(self)


class JiraUser(HttpLocust):
    host = JIRA_SETTINGS.server_url
    task_set = JiraBehavior
    wait_time = between(0, 0)
