from locust import HttpUser, task, between
from locustio.bamboo.http_actions import run_build_plans
from locustio.common_utils import LocustConfig, MyBaseTaskSet
from util.conf import BAMBOO_SETTINGS

config = LocustConfig(config_yml=BAMBOO_SETTINGS)


class BambooBehavior(MyBaseTaskSet):

    @task()
    def run_build_plans(self):
        run_build_plans(self)


class BambooUser(HttpUser):
    host = BAMBOO_SETTINGS.server_url
    tasks = [BambooBehavior]
    wait_time = between(0, 0)
