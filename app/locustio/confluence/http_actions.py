import itertools
import inspect
import logging
import random
import re

from locustio.common_utils import confluence_measure, fetch_by_re, timestamp_int,\
    TEXT_HEADERS, ADMIN_HEADERS, NO_TOKEN_HEADERS
from locustio.confluence.requests_params import confluence_datasets, Login, ViewPage


counter = itertools.count()
confluence_dataset = confluence_datasets()


@confluence_measure
def login_and_view_dashboard(locust):
    func_name = inspect.stack()[0][3]
    print(locust.logger)
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    user = random.choice(confluence_dataset["users"])
    username = user[0]
    password = user[1]

    params = Login()
    login_body = params.login_body
    login_body['os_username'] = username
    login_body['os_password'] = password
    locust.client.post('/dologin.action', login_body, TEXT_HEADERS, catch_response=True)
    r = locust.client.get('/', catch_response=True)
    content = r.content.decode('utf-8')
    assert 'Log Out' in content, f'Login with {username}, {password} failed.'
    locust.logger.info(f'User {username} is successfully logged in')
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    static_resource_url = fetch_by_re(params.static_resource_url_re, content)
    version_number = fetch_by_re(params.version_number_re, content)
    build_number = fetch_by_re(params.build_number_re, content)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("010"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get('/rest/mywork/latest/status/notification/count', catch_response=True)
    locust.client.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("025"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/experimental/search?cql=type=space%20and%20space.type=favourite%20order%20by%20favourite'
                      f'%20desc&expand=space.icon&limit=100&_={timestamp_int()}', catch_response=True)
    locust.client.get('/rest/dashboardmacros/1.0/updates?maxResults=40&tab=all&showProfilePic=true&labels='
                      '&spaces=&users=&types=&category=&spaceKey=', catch_response=True)


def view_page(locust):
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]
    params = ViewPage()

    @confluence_measure
    def view_page():
        r = locust.client.get(f'/pages/viewpage.action?pageId={page_id}', catch_response=True)
        content = r.content.decode('utf-8')
        assert 'Created by' and 'Save for later' in content, f'Fail to open page {page_id}'
        parent_page_id = fetch_by_re(params.parent_page_id_re, content)
        view_page_id = fetch_by_re(params.page_id_re, content)
        space_key = fetch_by_re(params.space_key_re, content)
        tree_request_id = fetch_by_re(params.tree_result_id_re, content)
        has_not_root = fetch_by_re(params.has_no_root_re, content)
        root_page_id = fetch_by_re(params.root_page_id_re, content)
        atl_token_view_issue = fetch_by_re(params.atl_token_view_issue_re, content)
        editable = fetch_by_re(params.editable_re, content)
        ancestor_ids = re.findall(params.ancestor_ids_re, content)
        locust.logger.info(f'Viewed page_id: {view_page_id}, parent_page_id: {parent_page_id}, space_key: {space_key},'
                           f'tree_request_id: {tree_request_id}, has_not_root: {has_not_root}, '
                           f'root_page_id: {root_page_id}, atlassian_token: {atl_token_view_issue}, '
                           f'page_editable: {editable}, ancestor_ids: {ancestor_ids}')
        locust.client.get('/rest/helptips/1.0/tips', catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("110"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/rest/likes/1.0/content/{page_id}/likes?commentLikes=true&_={timestamp_int()}',
                          catch_response=True)
        locust.client.get(f'/rest/highlighting/1.0/panel-items?pageId={page_id}&_={timestamp_int()}',
                          catch_response=True)
        locust.client.get(f'/rest/mywork/latest/status/notification/count?pageId={page_id}&_={timestamp_int()}',
                          catch_response=True)
        r = locust.client.get(f'/rest/inlinecomments/1.0/comments?containerId={page_id}&_={timestamp_int()}',
                          catch_response=True)
        content = r.content.decode('utf-8')
        assert 'authorDisplayName' or '[]' in content, f'Could not open comments for page {page_id}'
        locust.client.get(f'/plugins/editor-loader/editor.action?parentPageId={parent_page_id}&pageId={page_id}'
                          f'&spaceKey={space_key}&atl_after_login_redirect=/pages/viewpage.action'
                          f'&timeout=12000&_={timestamp_int()}')



    view_page()










