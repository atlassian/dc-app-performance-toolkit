# flake8: noqa
from locustio.common_utils import generate_random_string, read_input_file, BaseResource
from util.project_paths import CONFLUENCE_PAGES, CONFLUENCE_BLOGS, CONFLUENCE_USERS, CONFLUENCE_STATIC_CONTENT
import json


def confluence_datasets():
    data_sets = dict()
    data_sets["pages"] = read_input_file(CONFLUENCE_PAGES)
    data_sets["blogs"] = read_input_file(CONFLUENCE_BLOGS)
    data_sets["users"] = read_input_file(CONFLUENCE_USERS)
    data_sets['static-content'] = read_input_file(CONFLUENCE_STATIC_CONTENT)

    return data_sets


class ConfluenceResource(BaseResource):

    def __init__(self, resource_file='locustio/confluence/resources.json'):
        super().__init__(resource_file)
        
        
class Login(ConfluenceResource):
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


class ViewPage(ConfluenceResource):
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
    inline_comment_re = '\"id\":(.+?)\,\"'


class ViewDashboard(ConfluenceResource):
    action_name = 'view_dashboard'
    keyboard_hash_re = 'name=\"ajs-keyboardshortcut-hash\" content=\"(.*?)\">'
    static_resource_url_re = 'meta name=\"ajs-static-resource-url-prefix\" content=\"(.*?)/_\">'
    version_number_re = 'meta name=\"ajs-version-number\" content=\"(.*?)\">'
    build_number_re = 'meta name=\"ajs-build-number\" content=\"(.*?)\"'


class ViewBlog(ConfluenceResource):
    action_name = 'view_blog'
    parent_page_id_re = 'meta name=\"ajs-parent-page-id\" content=\"(.*?)\"'
    page_id_re = 'meta name=\"ajs-page-id\" content=\"(.*?)\">'
    space_key_re = 'meta id=\"confluence-space-key\" name=\"confluence-space-key\" content=\"(.*?)\"'
    atl_token_re = '"ajs-atl-token" content="(.+?)"'
    inline_comment_re = '\"id\":(.+?)\,\"'


class CreateBlog(ConfluenceResource):
    action_name = 'create_blog'
    atl_token_re = 'name=\"ajs-atl-token\" content=\"(.*?)\">'
    content_id_re = 'name=\"ajs-content-id\" content=\"(.*?)\">'
    space_key = 'createpage.action\?spaceKey=(.+?)\&'
    contribution_hash = '\"contributorsHash\":\"\"'

    created_blog_title_re = 'anonymous_export_view.*?\"webui\":\"(.*?)\"'


class CreateEditPage(ConfluenceResource):
    action_name = 'create_and_edit_page'
    content_id_re = 'meta name=\"ajs-content-id\" content=\"(.*?)\">'
    atl_token_re = 'meta name=\"ajs-atl-token\" content=\"(.*?)\">'
    space_key_re = 'createpage.action\?spaceKey=(.+?)\&'
    page_title_re = 'anonymous_export_view.*?\"webui\":\"(.*?)\"'
    page_id_re = 'meta name=\"ajs-page-id\" content=\"(.*?)\">'
    parent_page_id = 'meta name=\"ajs-parent-page-id\" content=\"(.*?)\"'
    create_page_id = 'meta name=\"ajs-page-id\" content=\"(.*?)\">'

    editor_page_title_re = 'name=\"ajs-page-title\" content=\"(.*?)\"'
    editor_page_version_re = 'name=\"ajs-page-version\" content=\"(.*?)\">'
    editor_page_content_re = 'id=\"wysiwygTextarea\" name=\"wysiwygContent\" class=\
                              "hidden tinymce-editor\">([\w\W]*?)</textarea>'


class CommentPage(ConfluenceResource):
    action_name = 'comment_page'


class UploadAttachments(ConfluenceResource):
    action_name = 'upload_attachments'
    atl_token_view_issue_re = '"ajs-atl-token" content="(.+?)"'


class LikePage(ConfluenceResource):
    action_name = 'like_page'
    like_re = '\{\"likes\":\[\{"user":\{"name\"\:\"(.+?)",'
