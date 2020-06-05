from locust import HttpLocust, TaskSet, task, between
from locustio.confluence.http_actions import login_and_view_dashboard, view_page, view_dashboard, view_blog, search_cql, create_blog
from locustio.common_utils import init_logger, ActionPercentage
from util.conf import CONFLUENCE_SETTINGS

action = ActionPercentage(config_yml=CONFLUENCE_SETTINGS)


class ConfluenceBehavior(TaskSet):

    def on_start(self):
        login_and_view_dashboard(self)

    # @task(action.percentage('view_page'))
    # def view_page(self):
    #     view_page(self)
    #
    # @task(action.percentage('view_dashboard'))
    @task(1)
    def view_dashboard(self):
        view_dashboard(self)

    # @task(action.percentage('view_blog'))
    # def view_blog(self):
    #     view_blog(self)
    #
    # @task(action.percentage('search_cql'))
    # def search_cql(self):
    #     search_cql(self)

    @task(action.percentage('create_blog'))
    def create_blog(self):
        create_blog(self)



    # @task(1)
    # def custom_action(self):
    #     custom_action(self)


class ConfluenceUser(HttpLocust):
    host = CONFLUENCE_SETTINGS.server_url
    task_set = ConfluenceBehavior
    wait_time = between(0, 0)
