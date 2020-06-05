import itertools
import inspect
import logging
import random
import re

from locustio.common_utils import confluence_measure, fetch_by_re, timestamp_int,\
    TEXT_HEADERS, ADMIN_HEADERS, NO_TOKEN_HEADERS, logger, generate_random_string, CONFLUENCE_SETTINGS
from locustio.confluence.requests_params import confluence_datasets, Login, ViewPage, ViewDashboard, ViewBlog, CreateBlog


confluence_dataset = confluence_datasets()


@confluence_measure
def login_and_view_dashboard(locust):
    params = Login()

    user = random.choice(confluence_dataset["users"])
    username = user[0]
    password = user[1]

    login_body = params.login_body
    login_body['os_username'] = username
    login_body['os_password'] = password
    locust.client.post('/dologin.action', login_body, TEXT_HEADERS, catch_response=True)
    r = locust.client.get('/', catch_response=True)
    content = r.content.decode('utf-8')
    assert 'Log Out' in content, f'Login with {username}, {password} failed.'
    logger.info(f'User {username} is successfully logged in')
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
    locust.storage = dict()  # Define locust storage dict for getting cross-functional variables access


def view_page(locust):
    params = ViewPage()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]

    @confluence_measure
    def view_page():
        r = locust.client.get(f'/pages/viewpage.action?pageId={page_id}', catch_response=True)
        content = r.content.decode('utf-8')
        assert 'Created by' and 'Save for later' in content, f'Fail to open page {page_id}'
        parent_page_id = fetch_by_re(params.parent_page_id_re, content)
        parsed_page_id = fetch_by_re(params.page_id_re, content)
        space_key = fetch_by_re(params.space_key_re, content)
        tree_request_id = fetch_by_re(params.tree_result_id_re, content)
        has_no_root = fetch_by_re(params.has_no_root_re, content)
        root_page_id = fetch_by_re(params.root_page_id_re, content)
        atl_token_view_issue = fetch_by_re(params.atl_token_view_issue_re, content)
        editable = fetch_by_re(params.editable_re, content)
        ancestor_ids = re.findall(params.ancestor_ids_re, content)

        ancestor_str = 'ancestors='
        for ancestor in ancestor_ids:
            ancestor_str = ancestor_str + str(ancestor) + '&'

        params.storage['page_id'] = parsed_page_id
        params.storage['has_no_root'] = has_no_root
        params.storage['tree_request_id'] = tree_request_id
        params.storage['root_page_id'] = root_page_id
        params.storage['ancestors'] = ancestor_str
        params.storage['space_key'] = space_key

        locust.client.get('/rest/helptips/1.0/tips', catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("110"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/rest/likes/1.0/content/{parsed_page_id}/likes?commentLikes=true&_={timestamp_int()}',
                          catch_response=True)
        locust.client.get(f'/rest/highlighting/1.0/panel-items?pageId={parsed_page_id}&_={timestamp_int()}',
                          catch_response=True)
        locust.client.get(f'/rest/mywork/latest/status/notification/count?pageId={parsed_page_id}&_={timestamp_int()}',
                          catch_response=True)
        r = locust.client.get(f'/rest/inlinecomments/1.0/comments?containerId={parsed_page_id}&_={timestamp_int()}',
                              catch_response=True)
        content = r.content.decode('utf-8')
        assert 'authorDisplayName' or '[]' in content, f'Could not open comments for page {parsed_page_id}'
        locust.client.get(f'/plugins/editor-loader/editor.action?parentPageId={parent_page_id}&pageId={parsed_page_id}'
                          f'&spaceKey={space_key}&atl_after_login_redirect=/pages/viewpage.action'
                          f'&timeout=12000&_={timestamp_int()}', catch_response=True)
        locust.client.get(f'/rest/watch-button/1.0/watchState/{parsed_page_id}?_={timestamp_int()}',
                          catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("145"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("150"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("155"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("160"),
                           TEXT_HEADERS, catch_response=True)

    @confluence_measure
    def view_page_tree():
        tree_request_id = params.storage['tree_request_id'].replace('&amp;', '&')
        ancestors = params.storage['ancestors']
        root_page_id = params.storage['root_page_id']
        viewed_page_id = params.storage['page_id']
        space_key = params.storage['space_key']
        r = ''
        # Page has parent
        if params.storage['has_no_root'] == 'false':
            request = f"{tree_request_id}&hasRoot=true&pageId={root_page_id}&treeId=0&startDepth=0&mobile=false" \
                      f"&{ancestors}treePageId={viewed_page_id}&_={timestamp_int()}"
            r = locust.client.get(f'{request}', catch_response=True)
        # Page does not have parent
        elif params.storage['has_no_root'] == 'true':
            request = f"{tree_request_id}&hasRoot=false&spaceKey={space_key}&treeId=0&startDepth=0&mobile=false" \
                      f"&{ancestors}treePageId={viewed_page_id}&_={timestamp_int()}"
            r = locust.client.get(f'{request}', catch_response=True)
        content = r.content.decode('utf-8')

        assert 'plugin_pagetree_children_span' and 'plugin_pagetree_children_list' in content

    view_page()
    view_page_tree()


@confluence_measure
def view_dashboard(locust):
    params = ViewDashboard()

    r = locust.client.get('/index.action', catch_response=True)
    content = r.content.decode('utf-8')
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    static_resource_url = fetch_by_re(params.static_resource_url_re, content)
    version_number = fetch_by_re(params.version_number_re, content)
    build_number = fetch_by_re(params.build_number_re, content)

    assert 'quick-search' and 'Log Out' in content
    locust.storage['build_number'] = build_number
    locust.storage['keyboard_hash'] = keyboard_hash

    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("205"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get('/rest/mywork/latest/status/notification/count', catch_response=True)
    locust.client.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}', catch_response=True)
    locust.client.get(f'/rest/experimental/search?cql=type=space%20and%20space.type=favourite%20order%20by%20'
                      f'favourite%20desc&expand=space.icon&limit=100&_={timestamp_int()}', catch_response=True)
    r = locust.client.get('/rest/dashboardmacros/1.0/updates?maxResults=40&tab=all&showProfilePic=true&labels='
                          '&spaces=&users=&types=&category=&spaceKey=', catch_response=True)
    assert 'changeSets' in r.content.decode('utf-8')


@confluence_measure
def view_blog(locust):
    params = ViewBlog()
    blog = random.choice(confluence_dataset["blogs"])
    blog_id = blog[0]

    r = locust.client.get(f'/pages/viewpage.action?pageId={blog_id}', catch_response=True)
    content = r.content.decode('utf-8')
    assert 'Created by' and 'Save for later' in content, f'Fail to open blog {blog_id}'

    parent_page_id = fetch_by_re(params.parent_page_id_re, content)
    parsed_blog_id = fetch_by_re(params.page_id_re, content)
    space_key = fetch_by_re(params.space_key_re, content)
    atl_token = fetch_by_re(params.atl_token_re, content)

    locust.client.get('/rest/helptips/1.0/tips', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("310"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/likes/1.0/content/{parsed_blog_id}/likes?commentLikes=true&_={timestamp_int()}',
                      catch_response=True)
    locust.client.get(f'/rest/highlighting/1.0/panel-items?pageId={parsed_blog_id}&_={timestamp_int()}',
                      catch_response=True)
    locust.client.get(f'/rest/mywork/latest/status/notification/count?pageId={parsed_blog_id}&_={timestamp_int()}',
                      catch_response=True)
    r = locust.client.get(f'/rest/inlinecomments/1.0/comments?containerId={parsed_blog_id}&_={timestamp_int()}',
                          catch_response=True)
    content = r.content.decode('utf-8')
    assert 'authorDisplayName' or '[]' in content, f'Could not open comments for page {parsed_blog_id}'

    r = locust.client.get(f'/plugins/editor-loader/editor.action?parentPageId={parent_page_id}&pageId={parsed_blog_id}'
                          f'&spaceKey={space_key}&atl_after_login_redirect=/pages/viewpage.action'
                          f'&timeout=12000&_={timestamp_int()}', catch_response=True)
    assert 'draftId' in r.content.decode('utf-8'), f'Could not open editor for blog {parsed_blog_id}'

    locust.client.get(f'/rest/watch-button/1.0/watchState/{parsed_blog_id}?_={timestamp_int()}', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("345"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("350"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("360"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("365"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/quickreload/latest/{parsed_blog_id}?since={timestamp_int()}&_={timestamp_int()}',
                      catch_response=True)


def search_cql(locust):

    @confluence_measure
    def recently_viewed():
        locust.client.get('/rest/recentlyviewed/1.0/recent?limit=8', catch_response=True)

    @confluence_measure
    def search_results():
        r = locust.client.get(f'/rest/api/search?cql=siteSearch~{generate_random_string(3, only_letters=True)}'
                              f'&start=0&limit=20', catch_response=True)
        if not '{"results":[' in r.content.decode('utf-8'):
            logger.info(r.content.decode('utf-8'))
        assert '{"results":[' in r.content.decode('utf-8')
        locust.client.get('/rest/mywork/latest/status/notification/count', catch_response=True)

    recently_viewed()
    search_results()


def create_blog(locust):
    params = CreateBlog()
    blog = random.choice(confluence_dataset["blogs"])
    blog_space_key = blog[1]
    build_number = locust.storage.get('build_number', '')
    keyboard_hash = locust.storage.get('keyboard_hash', '')

    @confluence_measure
    def create_blog_editor():
        r = locust.client.get(f'/pages/createblogpost.action?spaceKey={blog_space_key}', catch_response=True)
        content = r.content.decode('utf-8')
        assert 'Blog post title' in content, f'Could not open editor for {blog_space_key}'

        atl_token = fetch_by_re(params.atl_token_re, content)
        content_id = fetch_by_re(params.content_id_re, content)
        parsed_space_key = fetch_by_re(params.space_key, content)


        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("910"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/rest/mywork/latest/status/notification/count?pageId=0', catch_response=True)
        locust.client.get('/plugins/servlet/notifications-miniview', catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("925"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("930"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/rest/emoticons/1.0/_={timestamp_int()}', catch_response=True)
        locust.client.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}?_={timestamp_int()}',
                          catch_response=True)

        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "draftType": "blogpost",
                                   "spaceKey": parsed_space_key,
                                   "atl_token": atl_token
                                   }
        r = locust.client.post('/json/startheartbeatactivity.action', heartbeat_activity_body,
                               TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        assert atl_token in content

        contributor_hash = fetch_by_re(params.contribution_hash, content)
        params.storage['contributor_hash'] = contributor_hash

        r = locust.client.get(f'/rest/ui/1.0/content/{content_id}/labels', catch_response=True)
        assert '"success":true' in r.content.decode('utf-8'), f'Could not get labels for content {content_id}'

        draft_name = f"Performance Blog - {generate_random_string(10, only_letters=True)}"
        params.storage['draft_name'] = draft_name
        params.storage['parsed_space_key'] = parsed_space_key
        params.storage['content_id'] = content_id

        draft_body = {"draftId": content_id,
                      "pageId": "0",
                      "type": "blogpost",
                      "title": draft_name,
                      "spaceKey": parsed_space_key,
                      "content": "<p>test blog draft</p>",
                      "syncRev": "0.mcPCPtDvwoayMR7zvuQSbf8.27"}

        TEXT_HEADERS['Content-Type'] = 'application/json'
        r = locust.client.post('/rest/tinymce/1/drafts', json=draft_body, headers=TEXT_HEADERS, catch_response=True)
        assert 'draftId' in r.content.decode('utf-8'), f'Could not create blogpost draft in space {parsed_space_key}'

    @confluence_measure
    def create_blog():
        draft_name = params.storage['draft_name']
        parsed_space_key = params.storage['parsed_space_key']
        content_id = params.storage['content_id']
        draft_body = {"status": "current", "title": draft_name, "space": {"key": f"{parsed_space_key}"},
                      "body": {"editor": {"value": f"Test Performance Blog Page Content {draft_name}",
                                          "representation": "editor", "content": {"id": f"{content_id}"}}},
                      "id": f"{content_id}", "type": "blogpost",
                      "version": {"number": 1, "minorEdit": True, "syncRev": "0.mcPCPtDvwoayMR7zvuQSbf8.30"}}
        TEXT_HEADERS['Content-Type'] = 'application/json'
        r = locust.client.put(f'/rest/api/content/{content_id}?status=draft', json=draft_body,
                              headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        assert 'current' and 'title' in content, f'Could not open draft {draft_name} in space {parsed_space_key}'
        created_blog_title = fetch_by_re(params.created_blog_title_re, content)
        logger.info(f'Blog {created_blog_title} created')

        r = locust.client.get(f'/{created_blog_title}')
        assert 'Created by' in r.content.decode('utf-8'), f'Could not open created blog {created_blog_title}'



    create_blog_editor()
    create_blog()





















