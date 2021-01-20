from locustio.common_utils import read_input_file
import json
from util.project_paths import JSM_DATASET_CUSTOMERS, JSM_DATASET_REQUEST_TYPES, JSM_DATASET_SERVICE_DESKS_S


def jsm_customer_datasets():
    data_sets = dict()
    data_sets['customers'] = read_input_file(JSM_DATASET_CUSTOMERS)
    data_sets['s_portal'] = read_input_file(JSM_DATASET_SERVICE_DESKS_S)
    data_sets['request_types'] = read_input_file(JSM_DATASET_REQUEST_TYPES)

    return data_sets


class BaseResource:
    resources_file = 'locustio/jsm/customers/customers_resources.json'
    action_name = ''

    def __init__(self):
        self.resources_json = self.read_json()
        self.resources_body = self.action_resources()

    def read_json(self):
        with open(self.resources_file, encoding='UTF-8') as f:
            return json.load(f)

    def action_resources(self):
        return self.resources_json[self.action_name] if self.action_name in self.resources_json else dict()


class Login(BaseResource):
    action_name = 'login_and_view_portals'
    login_body = {
        'os_username': '',
        'os_password': '',
        'os_captcha': '',
        'os_cookie': 'true',
    }


class ViewPortal(BaseResource):
    action_name = 'view_portal'


class ViewRequests(BaseResource):
    action_name = 'view_requests'


class ViewRequest(BaseResource):
    action_name = 'view_request'


class AddComment(BaseResource):
    action_name = 'add_comment'


class ShareRequest(BaseResource):
    action_name = 'share_request'


class ShareRequestOrg(BaseResource):
    action_name = 'share_request_org'


class CreateRequest(BaseResource):
    action_name = 'create_request'
