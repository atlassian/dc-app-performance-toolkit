from locust import HttpLocust, TaskSet, task, between
from locustio.confluence.http_actions import login_and_view_dashboard, view_page_and_tree, view_dashboard, view_blog, \
    search_cql_and_view_results, open_editor_and_create_blog, create_and_edit_page, comment_page, view_attachments, \
    upload_attachments, like_page
from locustio.common_utils import ActionPercentage
from util.conf import CONFLUENCE_SETTINGS
from extension.confluence.extension_locust import app_specific_action

action = ActionPercentage(config_yml=CONFLUENCE_SETTINGS)


class ConfluenceBehavior(TaskSet):

    def on_start(self):
        login_and_view_dashboard(self)

    @task(action.percentage('view_page'))
    def view_page_action(self):
        view_page_and_tree(self)

    @task(action.percentage('view_dashboard'))
    def view_dashboard_action(self):
        view_dashboard(self)

    @task(action.percentage('view_blog'))
    def view_blog_action(self):
        view_blog(self)

    @task(action.percentage('search_cql'))
    def search_cql_action(self):
        search_cql_and_view_results(self)

    @task(action.percentage('create_blog'))
    def create_blog_action(self):
        open_editor_and_create_blog(self)

    @task(action.percentage('create_and_edit_page'))
    def create_and_edit_page_action(self):
        create_and_edit_page(self)

    @task(action.percentage('comment_page'))
    def comment_page_action(self):
        comment_page(self)

    @task(action.percentage('view_attachment'))
    def view_attachments_action(self):
        view_attachments(self)

    @task(action.percentage('upload_attachment'))
    def upload_attachments_action(self):
        upload_attachments(self)

    @task(action.percentage('like_page'))
    def like_page_action(self):
        like_page(self)

    @task(action.percentage('standalone_extension'))
    def custom_action(self):
        app_specific_action(self)


class ConfluenceUser(HttpLocust):
    host = CONFLUENCE_SETTINGS.server_url
    task_set = ConfluenceBehavior
    wait_time = between(0, 0)
