from locust import HttpUser, task, between
from locustio.jsm.customers import customers_http_actions
from locustio.common_utils import LocustConfig, MyBaseTaskSet
from extension.jsm.extension_locust_customers import app_specific_action
from util.conf import JSM_SETTINGS

config = LocustConfig(config_yml=JSM_SETTINGS)


class JsmCustomerBehavior(MyBaseTaskSet):

    def on_start(self):
        self.client.verify = config.secure
        customers_http_actions.customer_login_and_view_portals(self)

    @task(config.percentage('customer_view_portal'))
    def customer_view_portal(self):
        customers_http_actions.customer_view_portal(self)

    @task(config.percentage('customer_view_requests'))
    def customer_view_requests(self):
        customers_http_actions.customer_view_requests(self)

    @task(config.percentage('customer_view_request'))
    def customer_view_request(self):
        customers_http_actions.customer_view_request(self)

    @task(config.percentage('customer_add_comment'))
    def customer_add_comment(self):
        customers_http_actions.customer_add_comment(self)

    @task(config.percentage('customer_share_request_with_customer'))
    def customer_share_request_with_customer(self):
        customers_http_actions.customer_share_request_with_customer(self)

    @task(config.percentage('customer_share_request_with_org'))
    def customer_share_request_with_org(self):
        customers_http_actions.customer_share_request_with_org(self)

    @task(config.percentage('customer_create_request'))
    def customer_create_request(self):
        customers_http_actions.customer_create_request(self)

    @task(config.percentage('customer_standalone_extension'))  # By default disabled
    def custom_action(self):
        app_specific_action(self)


class JsmCustomer(HttpUser):
    host = JSM_SETTINGS.server_url
    tasks = [JsmCustomerBehavior]
    wait_time = between(0, 0)
