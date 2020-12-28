import random
import re

from locustio.common_utils import confluence_measure, fetch_by_re, timestamp_int, \
    TEXT_HEADERS, NO_TOKEN_HEADERS, JSON_HEADERS, RESOURCE_HEADERS, generate_random_string, init_logger, \
    raise_if_login_failed
from locustio.confluence.requests_params import confluence_datasets, Login, ViewPage, ViewDashboard, ViewBlog, \
    CreateBlog, CreateEditPage, UploadAttachments, LikePage
from util.conf import CONFLUENCE_SETTINGS
import uuid

logger = init_logger(app_type='confluence')
confluence_dataset = confluence_datasets()


@confluence_measure('locust_login_and_view_dashboard')
def login_and_view_dashboard(locust):
    session_id = str(uuid.uuid4())
    locust.cross_action_storage[session_id] = dict()
    locust.session_data_storage = locust.cross_action_storage[session_id]

    params = Login()
    user = random.choice(confluence_dataset["users"])
    username = user[0]
    password = user[1]

    login_body = params.login_body
    login_body['os_username'] = username
    login_body['os_password'] = password
    locust.post('/dologin.action', login_body, TEXT_HEADERS, catch_response=True)
    r = locust.get(url='/', catch_response=True)
    content = r.content.decode('utf-8')
    if 'Log Out' not in content:
        logger.error(f'Login with {username}, {password} failed: {content}')
    assert 'Log Out' in content, 'User authentication failed.'
    logger.locust_info(f'User {username} is successfully logged in')
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    build_number = fetch_by_re(params.build_number_re, content)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("010"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.get('/rest/mywork/latest/status/notification/count', catch_response=True)
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}', catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("025"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.get(f'/rest/experimental/search?cql=type=space%20and%20space.type=favourite%20order%20by%20favourite'
               f'%20desc&expand=space.icon&limit=100&_={timestamp_int()}', catch_response=True)
    locust.get('/rest/dashboardmacros/1.0/updates?maxResults=40&tab=all&showProfilePic=true&labels='
               '&spaces=&users=&types=&category=&spaceKey=', catch_response=True)

    locust.session_data_storage['build_number'] = build_number
    locust.session_data_storage['keyboard_hash'] = keyboard_hash
    locust.session_data_storage['username'] = username


def view_page_and_tree(locust):
    raise_if_login_failed(locust)
    params = ViewPage()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]

    @confluence_measure('locust_view_page:open_page')
    def view_page():
        r = locust.get(f'/pages/viewpage.action?pageId={page_id}', catch_response=True)
        content = r.content.decode('utf-8')
        if 'Created by' not in content or 'Save for later' not in content:
            logger.error(f'Fail to open page {page_id}: {content}')
        assert 'Created by' in content and 'Save for later' in content, 'Could not open page.'
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

        locust.session_data_storage['page_id'] = parsed_page_id
        locust.session_data_storage['has_no_root'] = has_no_root
        locust.session_data_storage['tree_request_id'] = tree_request_id
        locust.session_data_storage['root_page_id'] = root_page_id
        locust.session_data_storage['ancestors'] = ancestor_str
        locust.session_data_storage['space_key'] = space_key
        locust.session_data_storage['editable'] = editable
        locust.session_data_storage['atl_token_view_issue'] = atl_token_view_issue

        locust.get('/rest/helptips/1.0/tips', catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("110"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get(f'/rest/likes/1.0/content/{parsed_page_id}/likes?commentLikes=true&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/highlighting/1.0/panel-items?pageId={parsed_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/mywork/latest/status/notification/count?pageId={parsed_page_id}&_={timestamp_int()}',
                   catch_response=True)
        r = locust.get(f'/rest/inlinecomments/1.0/comments?containerId={parsed_page_id}&_={timestamp_int()}',
                       catch_response=True)
        content = r.content.decode('utf-8')
        if 'authorDisplayName' not in content and '[]' not in content:
            logger.error(f'Could not open comments for page {parsed_page_id}: {content}')
        assert 'authorDisplayName' in content or '[]' in content, 'Could not open comments for page.'
        locust.get(f'/plugins/editor-loader/editor.action?parentPageId={parent_page_id}&pageId={parsed_page_id}'
                   f'&spaceKey={space_key}&atl_after_login_redirect=/pages/viewpage.action'
                   f'&timeout=12000&_={timestamp_int()}', catch_response=True)
        locust.get(f'/rest/watch-button/1.0/watchState/{parsed_page_id}?_={timestamp_int()}',
                   catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("145"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("150"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("155"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("160"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    @confluence_measure('locust_view_page:view_page_tree')
    def view_page_tree():
        tree_request_id = locust.session_data_storage['tree_request_id'].replace('&amp;', '&')
        # if postfix is set, need to trim it from the tree_request_id to avoid duplication
        if tree_request_id.startswith(CONFLUENCE_SETTINGS.postfix):
            tree_request_id = tree_request_id[len(CONFLUENCE_SETTINGS.postfix):]
        ancestors = locust.session_data_storage['ancestors']
        root_page_id = locust.session_data_storage['root_page_id']
        viewed_page_id = locust.session_data_storage['page_id']
        space_key = locust.session_data_storage['space_key']
        r = ''
        # Page has parent
        if locust.session_data_storage['has_no_root'] == 'false':
            request = f"{tree_request_id}&hasRoot=true&pageId={root_page_id}&treeId=0&startDepth=0&mobile=false" \
                      f"&{ancestors}treePageId={viewed_page_id}&_={timestamp_int()}"
            r = locust.get(f'{request}', catch_response=True)
        # Page does not have parent
        elif locust.session_data_storage['has_no_root'] == 'true':
            request = f"{tree_request_id}&hasRoot=false&spaceKey={space_key}&treeId=0&startDepth=0&mobile=false" \
                      f"&{ancestors}treePageId={viewed_page_id}&_={timestamp_int()}"
            r = locust.get(f'{request}', catch_response=True)
        content = r.content.decode('utf-8')
        if 'plugin_pagetree_children_span' not in content or 'plugin_pagetree_children_list' not in content:
            logger.error(f'Could not view page tree: {content}')
        assert 'plugin_pagetree_children_span' in content and 'plugin_pagetree_children_list' in content, \
               'Could not view page tree.'

    view_page()
    view_page_tree()


@confluence_measure('locust_view_dashboard')
def view_dashboard(locust):
    raise_if_login_failed(locust)
    params = ViewDashboard()

    r = locust.get('/index.action', catch_response=True)
    content = r.content.decode('utf-8')
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    build_number = fetch_by_re(params.build_number_re, content)
    if 'quick-search' not in content or 'Log Out' not in content:
        logger.error(f'Could not view dashboard: {content}')
    assert 'quick-search' in content and 'Log Out' in content, 'Could not view dashboard.'

    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("205"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.get('/rest/mywork/latest/status/notification/count', catch_response=True)
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}', catch_response=True)
    locust.get(f'/rest/experimental/search?cql=type=space%20and%20space.type=favourite%20order%20by%20'
               f'favourite%20desc&expand=space.icon&limit=100&_={timestamp_int()}', catch_response=True)
    r = locust.get('/rest/dashboardmacros/1.0/updates?maxResults=40&tab=all&showProfilePic=true&labels='
                   '&spaces=&users=&types=&category=&spaceKey=', catch_response=True)
    content = r.content.decode('utf-8')
    if 'changeSets' not in content:
        logger.error(f'Could not view dashboard macros: {content}')
    assert 'changeSets' in content, 'Could not view dashboard macros.'


@confluence_measure('locust_view_blog')
def view_blog(locust):
    raise_if_login_failed(locust)
    params = ViewBlog()
    blog = random.choice(confluence_dataset["blogs"])
    blog_id = blog[0]

    r = locust.get(f'/pages/viewpage.action?pageId={blog_id}', catch_response=True)
    content = r.content.decode('utf-8')
    if 'Created by' not in content or 'Save for later' not in content:
        logger.error(f'Fail to open blog {blog_id}: {content}')
    assert 'Created by' in content and 'Save for later' in content, 'Could not view blog.'

    parent_page_id = fetch_by_re(params.parent_page_id_re, content)
    parsed_blog_id = fetch_by_re(params.page_id_re, content)
    space_key = fetch_by_re(params.space_key_re, content)

    locust.get('/rest/helptips/1.0/tips', catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("310"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.get(f'/rest/likes/1.0/content/{parsed_blog_id}/likes?commentLikes=true&_={timestamp_int()}',
               catch_response=True)
    locust.get(f'/rest/highlighting/1.0/panel-items?pageId={parsed_blog_id}&_={timestamp_int()}',
               catch_response=True)
    locust.get(f'/rest/mywork/latest/status/notification/count?pageId={parsed_blog_id}&_={timestamp_int()}',
               catch_response=True)
    r = locust.get(f'/rest/inlinecomments/1.0/comments?containerId={parsed_blog_id}&_={timestamp_int()}',
                   catch_response=True)
    content = r.content.decode('utf-8')
    if 'authorDisplayName' not in content and '[]' not in content:
        logger.error(f'Could not open comments for page {parsed_blog_id}: {content}')
    assert 'authorDisplayName' in content or '[]' in content, 'Could not open comments for page.'

    r = locust.get(f'/plugins/editor-loader/editor.action?parentPageId={parent_page_id}&pageId={parsed_blog_id}'
                   f'&spaceKey={space_key}&atl_after_login_redirect=/pages/viewpage.action'
                   f'&timeout=12000&_={timestamp_int()}', catch_response=True)
    content = r.content.decode('utf-8')
    if 'draftId' not in content:
        logger.error(f'Could not open editor for blog {parsed_blog_id}: {content}')
    assert 'draftId' in content, 'Could not open editor for blog.'

    locust.get(f'/rest/watch-button/1.0/watchState/{parsed_blog_id}?_={timestamp_int()}', catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("345"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("350"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("355"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("360"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.get(f'/rest/quickreload/latest/{parsed_blog_id}?since={timestamp_int()}&_={timestamp_int()}',
               catch_response=True)


def search_cql_and_view_results(locust):
    raise_if_login_failed(locust)

    @confluence_measure('locust_search_cql:recently_viewed')
    def search_recently_viewed():
        locust.get('/rest/recentlyviewed/1.0/recent?limit=8', catch_response=True)

    @confluence_measure('locust_search_cql:search_results')
    def search_cql():
        r = locust.get(f"/rest/api/search?cql=siteSearch~'{generate_random_string(3, only_letters=True)}'"
                       f"&start=0&limit=20", catch_response=True)
        if '{"results":[' not in r.content.decode('utf-8'):
            logger.locust_info(r.content.decode('utf-8'))
        content = r.content.decode('utf-8')
        if 'results' not in content:
            logger.error(f"Search cql failed: {content}")
        assert 'results' in content, "Search cql failed."
        locust.get('/rest/mywork/latest/status/notification/count', catch_response=True)

    search_recently_viewed()
    search_cql()


def open_editor_and_create_blog(locust):
    params = CreateBlog()
    blog = random.choice(confluence_dataset["blogs"])
    blog_space_key = blog[1]
    build_number = locust.session_data_storage.get('build_number', '')
    keyboard_hash = locust.session_data_storage.get('keyboard_hash', '')

    @confluence_measure('locust_create_blog:blog_editor')
    def create_blog_editor():
        raise_if_login_failed(locust)
        r = locust.get(f'/pages/createblogpost.action?spaceKey={blog_space_key}', catch_response=True)
        content = r.content.decode('utf-8')
        if 'Blog post title' not in content:
            logger.error(f'Could not open editor for {blog_space_key}: {content}')
        assert 'Blog post title' in content, 'Could not open editor for blog.'

        atl_token = fetch_by_re(params.atl_token_re, content)
        content_id = fetch_by_re(params.content_id_re, content)
        parsed_space_key = fetch_by_re(params.space_key, content)

        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("910"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get('/rest/mywork/latest/status/notification/count?pageId=0', catch_response=True)
        locust.get('/plugins/servlet/notifications-miniview', catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("925"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("930"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}?_={timestamp_int()}',
                   catch_response=True)

        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "draftType": "blogpost",
                                   "spaceKey": parsed_space_key,
                                   "atl_token": atl_token
                                   }
        r = locust.post('/json/startheartbeatactivity.action', heartbeat_activity_body,
                        TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if atl_token not in content:
            logger.error(f'Token {atl_token} not found in content: {content}')
        assert atl_token in content, 'Token not found in content.'

        contributor_hash = fetch_by_re(params.contribution_hash, content)
        locust.session_data_storage['contributor_hash'] = contributor_hash

        r = locust.get(f'/rest/ui/1.0/content/{content_id}/labels', catch_response=True)
        content = r.content.decode('utf-8')
        if '"success":true' not in content:
            logger.error(f'Could not get labels for content {content_id}: {content}')
        assert '"success":true' in content, 'Could not get labels for content in blog editor.'

        draft_name = f"Performance Blog - {generate_random_string(10, only_letters=True)}"
        locust.session_data_storage['draft_name'] = draft_name
        locust.session_data_storage['parsed_space_key'] = parsed_space_key
        locust.session_data_storage['content_id'] = content_id
        locust.session_data_storage['atl_token'] = atl_token

        draft_body = {"draftId": content_id,
                      "pageId": "0",
                      "type": "blogpost",
                      "title": draft_name,
                      "spaceKey": parsed_space_key,
                      "content": "<p>test blog draft</p>",
                      "syncRev": "0.mcPCPtDvwoayMR7zvuQSbf8.27"}

        TEXT_HEADERS['Content-Type'] = 'application/json'
        r = locust.post('/rest/tinymce/1/drafts', json=draft_body, headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if 'draftId' not in content:
            logger.error(f'Could not create blog post draft in space {parsed_space_key}: {content}')
        assert 'draftId' in content, 'Could not create blog post draft.'

    @confluence_measure('locust_create_blog:feel_and_publish')
    def create_blog():
        raise_if_login_failed(locust)
        draft_name = locust.session_data_storage['draft_name']
        parsed_space_key = locust.session_data_storage['parsed_space_key']
        content_id = locust.session_data_storage['content_id']
        atl_token = locust.session_data_storage['atl_token']

        draft_body = {"status": "current", "title": draft_name, "space": {"key": f"{parsed_space_key}"},
                      "body": {"editor": {"value": f"Test Performance Blog Page Content {draft_name}",
                                          "representation": "editor", "content": {"id": f"{content_id}"}}},
                      "id": f"{content_id}", "type": "blogpost",
                      "version": {"number": 1, "minorEdit": True, "syncRev": "0.mcPCPtDvwoayMR7zvuQSbf8.30"}}
        TEXT_HEADERS['Content-Type'] = 'application/json'
        r = locust.client.put(f'/rest/api/content/{content_id}?status=draft', json=draft_body,
                              headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if 'current' not in content or 'title' not in content:
            logger.error(f'Could not open draft {draft_name}: {content}')
        assert 'current' in content and 'title' in content, 'Could not open blog draft.'
        created_blog_title = fetch_by_re(params.created_blog_title_re, content)
        logger.locust_info(f'Blog {created_blog_title} created')

        r = locust.get(f'/{created_blog_title}', catch_response=True)
        content = r.content.decode('utf-8')
        if 'Created by' not in content:
            logger.error(f'Could not open created blog {created_blog_title}: {content}')
        assert 'Created by' in content, 'Could not open created blog.'

        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("970"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("975"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get('/plugins/servlet/notifications-miniview', catch_response=True)
        locust.get(f'/rest/watch-button/1.0/watchState/{content_id}?_={timestamp_int()}', catch_response=True)
        locust.get(f'/rest/likes/1.0/content/{content_id}/likes?commentLikes=true&_={timestamp_int()}',
                   catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("995"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get(f'/rest/highlighting/1.0/panel-items?pageId={content_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/inlinecomments/1.0/comments?containerId={content_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/s/en_GB/{build_number}/{keyboard_hash}/_/images/icons/profilepics/add_profile_pic.svg',
                   catch_response=True)
        locust.get('/rest/helptips/1.0/tips', catch_response=True)
        locust.get(f'/rest/mywork/latest/status/notification/count?pageid={content_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/plugins/editor-loader/editor.action?parentPageId=&pageId={content_id}'
                   f'&spaceKey={parsed_space_key}&atl_after_login_redirect={created_blog_title}'
                   f'&timeout=12000&_={timestamp_int()}', catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("1030"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("1035"),
                    headers=RESOURCE_HEADERS, catch_response=True)

        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "draftType": "blogpost",
                                   "spaceKey": parsed_space_key,
                                   "atl_token": atl_token
                                   }
        r = locust.post('/json/startheartbeatactivity.action', heartbeat_activity_body,
                        TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if atl_token not in content:
            logger.error(f'Token {atl_token} not found in content: {content}')
        assert atl_token in content, 'Token not found in content.'

    create_blog_editor()
    create_blog()


def create_and_edit_page(locust):
    params = CreateEditPage()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]
    space_key = page[1]
    build_number = locust.session_data_storage.get('build_number', '')
    keyboard_hash = locust.session_data_storage.get('keyboard_hash', '')

    @confluence_measure('locust_create_and_edit_page:create_page_editor')
    def create_page_editor():
        raise_if_login_failed(locust)
        r = locust.get(f'/pages/createpage.action?spaceKey={space_key}&fromPageId={page_id}&src=quick-create',
                       catch_response=True)
        content = r.content.decode('utf-8')
        if 'Page Title' not in content:
            logger.error(f'Could not open page editor: {content}')
        assert 'Page Title' in content, 'Could not open page editor.'

        parsed_space_key = fetch_by_re(params.space_key_re, content)
        atl_token = fetch_by_re(params.atl_token_re, content)
        content_id = fetch_by_re(params.content_id_re, content)
        locust.session_data_storage['content_id'] = content_id
        locust.session_data_storage['atl_token'] = atl_token

        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("705"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("710"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("715"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get('/rest/create-dialog/1.0/storage/quick-create', catch_response=True)
        locust.get(f'/rest/mywork/latest/status/notification/count?pageid=0&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/jiraanywhere/1.0/servers?_={timestamp_int()}', catch_response=True)
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}', catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("750"),
                    headers=RESOURCE_HEADERS, catch_response=True)

        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "draftType": "page",
                                   "spaceKey": parsed_space_key,
                                   "atl_token": atl_token
                                   }
        r = locust.post('/json/startheartbeatactivity.action', heartbeat_activity_body,
                        TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if atl_token not in content:
            logger.error(f'Token {atl_token} not found in content: {content}')
        assert atl_token in content, 'Token not found in content.'

    @confluence_measure('locust_create_and_edit_page:create_page')
    def create_page():
        raise_if_login_failed(locust)
        draft_name = f"{generate_random_string(10, only_letters=True)}"
        content_id = locust.session_data_storage['content_id']
        atl_token = locust.session_data_storage['atl_token']
        create_page_body = {
                            "status": "current",
                            "title": f"Test Performance JMeter {draft_name}",
                            "space": {"key": f"{space_key}"},
                            "body": {
                              "storage": {
                                "value": f"Test Performance Create Page Content {draft_name}",
                                "representation": "storage",
                                "content": {
                                  "id": f"{content_id}"
                                }
                              }
                            },
                            "id": f"{content_id}",
                            "type": "page",
                            "version": {
                              "number": 1
                            },
                            "ancestors": [
                              {
                                "id": f"{page_id}",
                                "type": "page"
                              }
                            ]
                        }

        TEXT_HEADERS['Content-Type'] = 'application/json'
        TEXT_HEADERS['X-Requested-With'] = 'XMLHttpRequest'
        r = locust.client.put(f'/rest/api/content/{content_id}?status=draft', json=create_page_body,
                              headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if 'draftId' not in content:
            logger.error(f'Could not create PAGE draft: {content}')
        assert 'draftId' in content, 'Could not create PAGE draft.'
        page_title = fetch_by_re(params.page_title_re, content)

        r = locust.get(f'{page_title}', catch_response=True)
        content = r.content.decode('utf-8')
        if 'Created by' not in content:
            logger.error(f'Page {page_title} was not created: {content}')
        assert 'Created by' in content, 'Page was not created.'

        parent_page_id = fetch_by_re(params.parent_page_id, content)
        create_page_id = fetch_by_re(params.create_page_id, content)
        locust.session_data_storage['create_page_id'] = create_page_id
        locust.session_data_storage['parent_page_id'] = parent_page_id

        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "space_key": space_key,
                                   "draftType": "page",
                                   "atl_token": atl_token
                                   }
        locust.post('/json/stopheartbeatactivity.action', params=heartbeat_activity_body,
                    headers=TEXT_HEADERS, catch_response=True)

        locust.get('/rest/helptips/1.0/tips', catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("795"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get(f'/rest/jira-metadata/1.0/metadata/aggregate?pageId={create_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/likes/1.0/content/{create_page_id}/likes?commentLikes=true&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/inlinecomments/1.0/comments?containerId={create_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/mywork/latest/status/notification/count?pageid={create_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/highlighting/1.0/panel-items?pageId={create_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/watch-button/1.0/watchState/{create_page_id}?_={timestamp_int()}',
                   catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("830"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("835"),
                    headers=RESOURCE_HEADERS, catch_response=True)

        r = locust.get(f'/plugins/editor-loader/editor.action?parentPageId={parent_page_id}'
                       f'&pageId={create_page_id}&spaceKey={space_key}'
                       f'&atl_after_login_redirect={page_title}&timeout=12000&_={timestamp_int()}',
                       catch_response=True)
        content = r.content.decode('utf-8')
        if page_title not in content:
            logger.error(f'Page editor load failed for page {page_title}: {content}')
        assert page_title in content, 'Page editor load failed for page.'

        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("845"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("850"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("855"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    @confluence_measure('locust_create_and_edit_page:open_editor')
    def open_editor():
        raise_if_login_failed(locust)
        create_page_id = locust.session_data_storage['create_page_id']

        r = locust.get(f'/pages/editpage.action?pageId={create_page_id}', catch_response=True)
        content = r.content.decode('utf-8')
        if '<title>Edit' not in content or 'Update</button>' not in content:
            logger.error(f'Could not open PAGE {create_page_id} to edit: {content}')
        assert '<title>Edit' in content and 'Update</button>' in content, \
               'Could not open PAGE to edit.'

        edit_page_version = fetch_by_re(params.editor_page_version_re, content)
        edit_atl_token = fetch_by_re(params.atl_token_re, content)
        edit_space_key = fetch_by_re(params.space_key_re, content)
        edit_content_id = fetch_by_re(params.content_id_re, content)
        edit_page_id = fetch_by_re(params.page_id_re, content)
        edit_parent_page_id = fetch_by_re(params.parent_page_id, content)

        locust.session_data_storage['edit_parent_page_id'] = edit_parent_page_id
        locust.session_data_storage['edit_page_version'] = edit_page_version
        locust.session_data_storage['edit_page_id'] = edit_page_id
        locust.session_data_storage['atl_token'] = edit_atl_token
        locust.session_data_storage['edit_content_id'] = edit_content_id

        locust.get(f'/rest/jiraanywhere/1.0/servers?_={timestamp_int()}', catch_response=True)
        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": edit_content_id,
                                   "draftType": "page",
                                   "spaceKey": edit_space_key,
                                   "atl_token": edit_atl_token
                                   }
        locust.post('/json/startheartbeatactivity.action', heartbeat_activity_body,
                    TEXT_HEADERS, catch_response=True)
        expand = 'history.createdBy.status%2Chistory.contributors.publishers.users.status' \
                 '%2Cchildren.comment.version.by.status'
        locust.get(f'/rest/api/content/{edit_page_id}?expand={expand}&_={timestamp_int()}',
                   catch_response=True)
        locust.post('/json/startheartbeatactivity.action', heartbeat_activity_body,
                    TEXT_HEADERS, catch_response=True)
        locust.get(f'/rest/ui/1.0/content/{edit_page_id}/labels?_={timestamp_int()}', catch_response=True)
        locust.get('/rest/mywork/latest/status/notification/count', catch_response=True)
        locust.post('/json/startheartbeatactivity.action', heartbeat_activity_body,
                    TEXT_HEADERS, catch_response=True)

    @confluence_measure('locust_create_and_edit_page:edit_page')
    def edit_page():
        raise_if_login_failed(locust)
        locust.session_data_storage['draft_name'] = f"{generate_random_string(10, only_letters=True)}"
        edit_parent_page_id = locust.session_data_storage['edit_parent_page_id']
        edit_page_id = locust.session_data_storage['edit_page_id']
        content_id = locust.session_data_storage['edit_content_id']
        edit_page_version = int(locust.session_data_storage['edit_page_version']) + 1
        edit_atl_token = locust.session_data_storage['atl_token']
        edit_page_body = dict()

        if edit_parent_page_id:
            edit_page_body = {
                  "status": "current",
                  "title": f"Test Performance Edit with locust {locust.session_data_storage['draft_name']}",
                  "space": {
                    "key": f"{space_key}"
                  },
                  "body": {
                    "storage": {
                      "value": f"Page edit with locust {locust.session_data_storage['draft_name']}",
                      "representation": "storage",
                      "content": {
                        "id": f"{content_id}"
                      }
                    }
                  },
                  "id": f"{content_id}",
                  "type": "page",
                  "version": {
                    "number": f"{edit_page_version}"
                  },
                  "ancestors": [
                    {
                      "id": f"{edit_parent_page_id}",
                      "type": "page"
                    }
                  ]
                }

        if not edit_parent_page_id:
            edit_page_body = {
                              "status": "current",
                              "title": f"Test Performance Edit with locust {locust.session_data_storage['draft_name']}",
                              "space": {
                                "key": f"{space_key}"
                              },
                              "body": {
                                "storage": {
                                  "value": f"Page edit with locust {locust.session_data_storage['draft_name']}",
                                  "representation": "storage",
                                  "content": {
                                    "id": f"{content_id}"
                                  }
                                }
                              },
                              "id": f"{content_id}",
                              "type": "page",
                              "version": {
                                "number": f"{edit_page_version}"
                              }
                            }
        TEXT_HEADERS['Content-Type'] = 'application/json'
        TEXT_HEADERS['X-Requested-With'] = 'XMLHttpRequest'
        r = locust.client.put(f'/rest/api/content/{content_id}?status=draft', json=edit_page_body,
                              headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')

        if 'history' not in content:
            logger.info(f'Could not edit page. Response content: {content}')
        if 'history' not in content:
            logger.error(f'User {locust.session_data_storage["username"]} could not edit page {content_id}, '
                         f'parent page id: {edit_parent_page_id}: {content}')
        assert 'history' in content, \
               'User could not edit page.'

        r = locust.get(f'/pages/viewpage.action?pageId={edit_page_id}', catch_response=True)
        content = r.content.decode('utf-8')
        if not('last-modified' in content and 'Created by' in content):
            logger.error(f"Could not open page {edit_page_id}: {content}")
        assert 'last-modified' in content and 'Created by' in content, "Could not open page to edit."

        locust.get('/rest/mywork/latest/status/notification/count', catch_response=True)
        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "space_key": space_key,
                                   "draftType": "page",
                                   "atl_token": edit_atl_token
                                   }
        locust.post('/json/stopheartbeatactivity.action', params=heartbeat_activity_body,
                    headers=TEXT_HEADERS, catch_response=True)
        locust.get('/rest/helptips/1.0/tips', catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("1175"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.get(f'/rest/jira-metadata/1.0/metadata/aggregate?pageId={edit_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/likes/1.0/content/{edit_page_id}/likes?commentLikes=true&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/highlighting/1.0/panel-items?pageId={edit_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/mywork/latest/status/notification/count?pageId={edit_page_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/plugins/editor-loader/editor.action?parentPageId={edit_parent_page_id}'
                   f'&pageId={edit_page_id}&spaceKey={space_key}&atl_after_login_redirect=/pages/viewpage.action'
                   f'&timeout=12000&_={timestamp_int()}', catch_response=True)
        locust.get(f'/rest/inlinecomments/1.0/comments?containerId={content_id}&_={timestamp_int()}',
                   catch_response=True)
        locust.get(f'/rest/watch-button/1.0/watchState/{edit_page_id}?_={timestamp_int()}',
                   catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("1215"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("1220"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("1225"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("1230"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    create_page_editor()
    create_page()
    open_editor()
    edit_page()


@confluence_measure('locust_comment_page')
def comment_page(locust):
    raise_if_login_failed(locust)
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]
    comment = f'<p>{generate_random_string(length=15, only_letters=True)}</p>'
    uid = str(uuid.uuid4())
    r = locust.post(f'/rest/tinymce/1/content/{page_id}/comment?actions=true',
                    params={'html': comment, 'watch': True, 'uuid': uid}, headers=NO_TOKEN_HEADERS,
                    catch_response=True)
    content = r.content.decode('utf-8')
    if not('reply-comment' in content and 'edit-comment' in content):
        logger.error(f'Could not add comment: {content}')
    assert 'reply-comment' in content and 'edit-comment' in content, 'Could not add comment.'


@confluence_measure('locust_view_attachment')
def view_attachments(locust):
    raise_if_login_failed(locust)
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]
    r = locust.get(f'/pages/viewpageattachments.action?pageId={page_id}', catch_response=True)
    content = r.content.decode('utf-8')
    if not('Upload file' in content and 'Attach more files' in content or 'currently no attachments' in content):
        logger.error(f'View attachments failed: {content}')
    assert 'Upload file' in content and 'Attach more files' in content \
           or 'currently no attachments' in content, 'View attachments failed.'


@confluence_measure('locust_upload_attachment')
def upload_attachments(locust):
    raise_if_login_failed(locust)
    params = UploadAttachments()
    page = random.choice(confluence_dataset["pages"])
    static_content = random.choice(confluence_dataset["static-content"])
    file_path = static_content[0]
    file_name = static_content[2]
    file_extension = static_content[1]
    page_id = page[0]

    r = locust.get(f'/pages/viewpage.action?pageId={page_id}', catch_response=True)
    content = r.content.decode('utf-8')
    if not('Created by' in content and 'Save for later' in content):
        logger.error(f'Failed to open page {page_id}: {content}')
    assert 'Created by' in content and 'Save for later' in content, 'Failed to open page to upload attachments.'
    atl_token_view_issue = fetch_by_re(params.atl_token_view_issue_re, content)

    multipart_form_data = {
        "file": (file_name, open(file_path, 'rb'), file_extension)
    }

    r = locust.post(f'/pages/doattachfile.action?pageId={page_id}',
                    params={"atl_token": atl_token_view_issue, "comment_0": "", "comment_1": "", "comment_2": "",
                            "comment_3": "", "comment_4": "0", "confirm": "Attach"}, files=multipart_form_data,
                    catch_response=True)
    content = r.content.decode('utf-8')
    if not('Upload file' in content and 'Attach more files' in content):
        logger.error(f'Could not upload attachments: {content}')
    assert 'Upload file' in content and 'Attach more files' in content, 'Could not upload attachments.'


@confluence_measure('locust_like_page')
def like_page(locust):
    raise_if_login_failed(locust)
    params = LikePage()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]

    JSON_HEADERS['Origin'] = CONFLUENCE_SETTINGS.server_url
    r = locust.get(f'/rest/likes/1.0/content/{page_id}/likes', headers=JSON_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')
    like = fetch_by_re(params.like_re, content)

    if like is None:
        r = locust.post(f'/rest/likes/1.0/content/{page_id}/likes', headers=JSON_HEADERS, catch_response=True)
    else:
        r = locust.client.delete(f'/rest/likes/1.0/content/{page_id}/likes', catch_response=True)

    content = r.content.decode('utf-8')
    if 'likes' not in content:
        logger.error(f"Could not set like to the page {page_id}: {content}")
    assert 'likes' in r.content.decode('utf-8'), 'Could not set like to the page.'
