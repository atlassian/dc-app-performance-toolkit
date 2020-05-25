from locustio.common_utils import generate_random_string, read_input_file
from util.project_paths import CONFLUENCE_PAGES, CONFLUENCE_BLOGS, CONFLUENCE_USERS
import json


def confluence_datasets():
    data_sets = dict()
    data_sets["pages"] = read_input_file(CONFLUENCE_PAGES)
    data_sets["blogs"] = read_input_file(CONFLUENCE_BLOGS)
    data_sets["users"] = read_input_file(CONFLUENCE_USERS)
    return data_sets


class BaseResource:
    resources_file = 'locustio/jira/resources.json'
    action_name = ''

    def __init__(self):
        self.resources_json = self.read_json()
        self.body = self.action_resources()

    def read_json(self):
        with open(self.resources_file) as f:
            return json.load(f)

    def action_resources(self):
        return self.resources_json[self.action_name] if self.action_name in self.resources_json else dict()


class Login(BaseResource):
    action_name = 'login_and_view_dashboard'
    login_body = {
        'os_username': '',
        'os_password': '',
        'os_cookie': True,
        'os_destination': '',
        'login': 'Log in'
    }
    keyboard_hash_re = 'name=\"ajs-keyboardshortcut-hash\" content=\"(.*?)\">'
    static_resource_url_re = 'meta name=\"ajs-static-resource-url-prefix\" content=\"(.*?)/_\">'
    version_number_re = 'meta name=\"ajs-version-number\" content=\"(.*?)\">'
    build_number_re = 'meta name=\"ajs-build-number\" content=\"(.*?)\"'


class ViewPage(BaseResource):
    action_name = 'view_page'
    parent_page_id_re = 'meta name=\"ajs-parent-page-id\" content=\"(.*?)\"'
    page_id_re = 'meta name=\"ajs-page-id\" content=\"(.*?)\">'
    space_key_re = 'meta id=\"confluence-space-key\" name=\"confluence-space-key\" content=\"(.*?)\"'
    ancestor_ids_re = 'name=\"ancestorId\" value=\"(.*?)\"'
    tree_result_id_re = 'name="treeRequestId" value="(.+?)"'
    has_no_root_re = '"noRoot" value="(.+?)"'
    root_page_id_re = 'name="rootPageId" value="(.+?)"'
    atl_token_view_issue_re = '"ajs-atl-token" content="(.+?)"'
    editable_re = 'id=\"editPageLink\" href="(.+?)\?pageId=(.+?)\"'



