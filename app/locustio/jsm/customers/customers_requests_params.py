from locustio.common_utils import read_input_file, BaseResource
import json
from util.project_paths import JSM_DATASET_CUSTOMERS, JSM_DATASET_REQUEST_TYPES, JSM_DATASET_SERVICE_DESKS_S


def jsm_customer_datasets():
    data_sets = dict()
    data_sets['customers'] = read_input_file(JSM_DATASET_CUSTOMERS)
    data_sets['s_portal'] = read_input_file(JSM_DATASET_SERVICE_DESKS_S)
    data_sets['request_types'] = read_input_file(JSM_DATASET_REQUEST_TYPES)

    return data_sets


class JsmCustomersResource(BaseResource):

    def __init__(self, resource_file='locustio/jsm/customers/customers_resources.json'):
        super().__init__(resource_file)
        

class Login(JsmCustomersResource):
    action_name = 'login_and_view_portals'
    login_body = {
        'os_username': '',
        'os_password': '',
        'os_captcha': '',
        'os_cookie': 'true',
    }


class ViewPortal(JsmCustomersResource):
    action_name = 'view_portal'


class ViewRequests(JsmCustomersResource):
    action_name = 'view_requests'


class ViewRequest(JsmCustomersResource):
    action_name = 'view_request'


class AddComment(JsmCustomersResource):
    action_name = 'add_comment'


class ShareRequest(JsmCustomersResource):
    action_name = 'share_request'


class ShareRequestOrg(JsmCustomersResource):
    action_name = 'share_request_org'


class CreateRequest(JsmCustomersResource):
    action_name = 'create_request'
