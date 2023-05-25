from locust import HttpUser, task, between
from extension.bamboo.extension_locust import app_specific_action
from locustio.bamboo.http_actions import locust_bamboo_login
from locustio.common_utils import LocustConfig, MyBaseTaskSet
from util.conf import BAMBOO_SETTINGS

config = LocustConfig(config_yml=BAMBOO_SETTINGS)


class BambooBehavior(MyBaseTaskSet):

    def on_start(self):
        self.client.verify = config.secure
        locust_bamboo_login(self)

    @task(config.percentage('standalone_extension_locust'))
    def custom_action(self):
        app_specific_action(self)


class BambooUser(HttpUser):
    host = BAMBOO_SETTINGS.server_url
    tasks = [BambooBehavior]
    wait_time = between(0, 0)
