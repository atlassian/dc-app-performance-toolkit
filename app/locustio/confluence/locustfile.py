import inspect

from locust import HttpUser, TaskSet, task, between
from locustio.confluence.http_actions import login_and_view_dashboard, view_page_and_tree, view_dashboard, view_blog, \
    search_cql_and_view_results, open_editor_and_create_blog, create_and_edit_page, comment_page, view_attachments, \
    upload_attachments, like_page
from locustio.common_utils import LocustConfig
from util.conf import CONFLUENCE_SETTINGS
from extension.confluence.extension_locust import app_specific_action
from locust import events

config = LocustConfig(config_yml=CONFLUENCE_SETTINGS)


class MyBaseTaskSet(TaskSet):

    cross_action_storage = dict()  # Cross actions locust storage
    login_failed = False

    def failure_check(self, response, action_name):
        if not response:
            if 'login' in action_name:
                self.login_failed = True
            events.request_failure.fire(request_type="Action",
                                        name=f"locust_{action_name}",
                                        response_time=0,
                                        response_length=0,
                                        exception=str(response.raise_for_status()))

    def get(self, *args, **kwargs):
        r = self.client.get(*args, **kwargs)
        action_name = inspect.stack()[1][3]
        self.failure_check(response=r, action_name=action_name)
        return r

    def post(self, *args, **kwargs):
        r = self.client.post(*args, **kwargs)
        action_name = inspect.stack()[1][3]
        self.failure_check(response=r, action_name=action_name)
        return r


class ConfluenceBehavior(MyBaseTaskSet):

    def on_start(self):
        self.client.verify = config.secure
        login_and_view_dashboard(self)

    @task(config.percentage('view_page'))
    def view_page_action(self):
        view_page_and_tree(self)

    @task(config.percentage('view_dashboard'))
    def view_dashboard_action(self):
        view_dashboard(self)

    @task(config.percentage('view_blog'))
    def view_blog_action(self):
        view_blog(self)

    @task(config.percentage('search_cql'))
    def search_cql_action(self):
        search_cql_and_view_results(self)

    @task(config.percentage('create_blog'))
    def create_blog_action(self):
        open_editor_and_create_blog(self)

    @task(config.percentage('create_and_edit_page'))
    def create_and_edit_page_action(self):
        create_and_edit_page(self)

    @task(config.percentage('comment_page'))
    def comment_page_action(self):
        comment_page(self)

    @task(config.percentage('view_attachment'))
    def view_attachments_action(self):
        view_attachments(self)

    @task(config.percentage('upload_attachment'))
    def upload_attachments_action(self):
        upload_attachments(self)

    @task(config.percentage('like_page'))
    def like_page_action(self):
        like_page(self)

    @task(config.percentage('standalone_extension'))
    def custom_action(self):
        app_specific_action(self)


class ConfluenceUser(HttpUser):
    host = CONFLUENCE_SETTINGS.server_url
    tasks = [ConfluenceBehavior]
    wait_time = between(0, 0)
