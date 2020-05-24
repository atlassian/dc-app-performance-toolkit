from locust import HttpLocust, TaskSet, task, between
from locustio.confluence.http_actions import *
from locustio.common_utils import init_logger
from util.conf import CONFLUENCE_SETTINGS

init_logger()


class ConfluenceBehavior(TaskSet):

    def on_start(self):
        login_and_view_dashboard(self)


    # @task(1)
    # def custom_action(self):
    #     custom_action(self)


class JiraUser(HttpLocust):
    host = CONFLUENCE_SETTINGS.server_url
    task_set = ConfluenceBehavior
    wait_time = between(0, 0)
