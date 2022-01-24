from locustio.common_utils import read_input_file
from util.project_paths import BAMBOO_USERS, BAMBOO_BUILD_PLANS


class Login:
    action_name = 'jmeter_login_and_view_all_builds'
    atl_token_pattern = r'name="atlassian-token" content="(.+?)">'
    login_body = {
        'os_username': '',
        'os_password': '',
        'os_destination': '',
        'save': 'Log in',
        'atl_token': '',
    }


def bamboo_datasets():
    data_sets = dict()
    data_sets["users"] = read_input_file(BAMBOO_USERS)
    data_sets["build_plans"] = read_input_file(BAMBOO_BUILD_PLANS)
    return data_sets
