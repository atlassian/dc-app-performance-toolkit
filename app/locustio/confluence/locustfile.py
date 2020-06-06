from locust import HttpLocust, TaskSet, task, between
from locustio.confluence.http_actions import login_and_view_dashboard, view_page, view_dashboard, view_blog, \
    search_cql, create_blog, create_and_edit_page, comment_page, view_attachments, upload_attachments, like_page
from locustio.common_utils import ActionPercentage
from util.conf import CONFLUENCE_SETTINGS

action = ActionPercentage(config_yml=CONFLUENCE_SETTINGS)


class ConfluenceBehavior(TaskSet):

    def on_start(self):
        login_and_view_dashboard(self)

    @task(action.percentage('view_page'))
    def view_page(self):
        view_page(self)

    @task(action.percentage('view_dashboard'))
    def view_dashboard(self):
        view_dashboard(self)

    @task(action.percentage('view_blog'))
    def view_blog(self):
        view_blog(self)

    @task(action.percentage('search_cql'))
    def search_cql(self):
        search_cql(self)

    @task(action.percentage('create_blog'))
    def create_blog(self):
        create_blog(self)

    @task(action.percentage('create_and_edit_page'))
    def create_and_edit_page(self):
        create_and_edit_page(self)

    @task(action.percentage('comment_page'))
    def comment_page(self):
        comment_page(self)

    @task(action.percentage('view_attachments'))
    def view_attachments(self):
        view_attachments(self)

    @task(action.percentage('upload_attachments'))
    def upload_attachments(self):
        upload_attachments(self)

    @task(action.percentage('like_page'))
    def like_page(self):
        like_page(self)

    # @task(1)
    # def custom_action(self):
    #     custom_action(self)


class ConfluenceUser(HttpLocust):
    host = CONFLUENCE_SETTINGS.server_url
    task_set = ConfluenceBehavior
    wait_time = between(0, 0)
