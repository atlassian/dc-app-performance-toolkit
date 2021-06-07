import random
import re

from locustio.common_utils import confluence_measure, fetch_by_re, timestamp_int, \
    TEXT_HEADERS, NO_TOKEN_HEADERS, JSON_HEADERS, RESOURCE_HEADERS, generate_random_string, init_logger, \
    raise_if_login_failed
from locustio.confluence.requests_params import confluence_datasets, Login, ViewPage, ViewDashboard, ViewBlog, \
    CreateBlog, CreateEditPage, UploadAttachments, LikePage, CommentPage, ViewAttachment
from util.conf import CONFLUENCE_SETTINGS
import uuid

logger = init_logger(app_type='confluence')
confluence_dataset = confluence_datasets()


@confluence_measure('locust_login_and_view_dashboard')
def login_and_view_dashboard(locust):
    session_id = str(uuid.uuid4())
    locust.cross_action_storage[session_id] = dict()
    locust.session_data_storage = locust.cross_action_storage[session_id]
    locust.session_data_storage['app'] = 'confluence'

    params = Login()
    user = random.choice(confluence_dataset["users"])
    username = user[0]
    password = user[1]

    login_body = params.login_body
    login_body['os_username'] = username
    login_body['os_password'] = password

    # 10 dologin.action
    locust.post('/dologin.action',
                login_body,
                TEXT_HEADERS,
                catch_response=True)

    r = locust.get(url='/', catch_response=True)
    content = r.content.decode('utf-8')

    if 'Log Out' not in content:
        logger.error(f'Login with {username}, {password} failed: {content}')
    assert 'Log Out' in content, 'User authentication failed.'
    logger.locust_info(f'User {username} is successfully logged in')
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    build_number = fetch_by_re(params.build_number_re, content)
    token = fetch_by_re(params.atl_token_pattern, content)

    # 20 index.action
    locust.get('/index.action', catch_response=True)

    # 30 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("30"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 40 rest/shortcuts/latest/shortcuts/{ajs-build-number}/{ajs-keyboardshortcut-hash}
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}', catch_response=True)

    # 50 rest/mywork/latest/status/notification/count
    locust.get('/rest/mywork/latest/status/notification/count', catch_response=True)

    # 60 rest/dashboardmacros/1.0/updates
    locust.get('/rest/dashboardmacros/1.0/updates?maxResults=40&tab=all&showProfilePic=true&labels='
               '&spaces=&users=&types=&category=&spaceKey=',
               catch_response=True)

    # 70 rest/experimental/search
    locust.get(f'/rest/experimental/search?cql=type=space%20and%20space.type=favourite%20order%20by%20'
               f'favourite%20desc&expand=space.icon&limit=100&_={timestamp_int()}',
               catch_response=True)

    # 80 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("80"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 90 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("90"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    locust.session_data_storage['build_number'] = build_number
    locust.session_data_storage['keyboard_hash'] = keyboard_hash
    locust.session_data_storage['username'] = user[0]
    locust.session_data_storage['password'] = user[1]
    locust.session_data_storage['token'] = token


@confluence_measure('locust_view_page')
def view_page(locust):
    raise_if_login_failed(locust)
    params = ViewPage()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]

    # 100 pages/viewpage.action
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

    # 110 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("110"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 120 rest/helptips/1.0/tips
    locust.get('/rest/helptips/1.0/tips', catch_response=True)

    # 130 rest/inlinecomments/1.0/comments
    r = locust.get(f'/rest/inlinecomments/1.0/comments'
                   f'?containerId={parsed_page_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)
    content = r.content.decode('utf-8')
    if 'authorDisplayName' not in content and '[]' not in content:
        logger.error(f'Could not open comments for page {parsed_page_id}: {content}')
    assert 'authorDisplayName' in content or '[]' in content, 'Could not open comments for page.'

    # 140 rest/shortcuts/latest/shortcuts/{ajs-build-number}/{ajs-keyboardshortcut-hash}
    locust.get(f'/rest/shortcuts/latest/shortcuts/'
               f'{locust.session_data_storage["build_number"]}/'
               f'{locust.session_data_storage["keyboard_hash"]}',
               catch_response=True)

    # 150 plugins/pagetree/naturalchildren.action
    locust.get(f'/plugins/pagetree/naturalchildren.action'
               f'?decorator=none'
               f'&expandCurrent=true'
               f'&mobile=false'
               f'&sort=position'
               f'&reverse=false'
               f'&spaceKey={space_key}'
               f'&treeId=0'
               f'&hasRoot=false'
               f'&startDepth=0'
               f'&disableLinks=false'
               f'&placement=sidebar'
               f'&excerpt=false'
               f'&ancestors={parent_page_id}'
               f'&treePageId={parsed_page_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 160 rest/likes/1.0/content/{page_id}/likes
    locust.get(f'/rest/likes/1.0/content/{parsed_page_id}/likes'
               f'?commentLikes=true'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 170 rest/highlighting/1.0/panel-items
    locust.get(f'/rest/highlighting/1.0/panel-items'
               f'?pageId={parsed_page_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 180 rest/mywork/latest/status/notification/count
    locust.get(f'/rest/mywork/latest/status/notification/count'
               f'?pageId={parsed_page_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 190 rest/watch-button/1.0/watchState/${page_id}
    locust.get(f'/rest/watch-button/1.0/watchState/{parsed_page_id}'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 200 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("200"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 210 plugins/editor-loader/editor.action
    locust.get(f'/plugins/editor-loader/editor.action'
               f'?parentPageId={parent_page_id}'
               f'&pageId={parsed_page_id}'
               f'&spaceKey={space_key}'
               f'&atl_after_login_redirect=/pages/viewpage.action'
               f'&timeout=12000&_={timestamp_int()}',
               catch_response=True)

    # 220 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("220"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 230 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("230"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 240 plugins/macrobrowser/browse-macros.action
    locust.get('/plugins/macrobrowser/browse-macros.action'
               '?macroMetadataClientCacheKey=1618567304880'
               '&detailed=false',
               catch_response=True)


@confluence_measure('locust_view_dashboard')
def view_dashboard(locust):
    raise_if_login_failed(locust)
    params = ViewDashboard()

    # 270 index.action
    r = locust.get('/index.action', catch_response=True)

    content = r.content.decode('utf-8')
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    build_number = fetch_by_re(params.build_number_re, content)
    if 'quick-search' not in content or 'Log Out' not in content:
        logger.error(f'Could not view dashboard: {content}')
    assert 'quick-search' in content and 'Log Out' in content, 'Could not view dashboard.'

    # 280 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("280"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 290 rest/shortcuts/latest/shortcuts/${ajs-build-number}/${ajs-keyboardshortcut-hash}
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}', catch_response=True)

    # 300 rest/mywork/latest/status/notification/count
    locust.get('/rest/mywork/latest/status/notification/count', catch_response=True)

    # 310 rest/dashboardmacros/1.0/updates
    r = locust.get('/rest/dashboardmacros/1.0/updates'
                   '?maxResults=40'
                   '&tab=all'
                   '&showProfilePic=true&'
                   'labels='
                   '&spaces='
                   '&users='
                   '&types='
                   '&category='
                   '&spaceKey=',
                   catch_response=True)

    content = r.content.decode('utf-8')
    if 'changeSets' not in content:
        logger.error(f'Could not view dashboard macros: {content}')
    assert 'changeSets' in content, 'Could not view dashboard macros.'

    # 320 rest/experimental/search
    locust.get(f'/rest/experimental/search'
               f'?cql=type=space%20and%20space.type=favourite%20order%20by%20favourite%20desc'
               f'&expand=space.icon'
               f'&limit=100'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 330 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("330"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


@confluence_measure('locust_view_blog')
def view_blog(locust):
    raise_if_login_failed(locust)
    params = ViewBlog()
    blog = random.choice(confluence_dataset["blogs"])
    blog_id = blog[0]

    # 340 pages/viewpage.action
    r = locust.get(f'/pages/viewpage.action'
                   f'?pageId={blog_id}',
                   catch_response=True)

    content = r.content.decode('utf-8')
    if 'Created by' not in content or 'Save for later' not in content:
        logger.error(f'Fail to open blog {blog_id}: {content}')
    assert 'Created by' in content and 'Save for later' in content, 'Could not view blog.'

    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    build_number = fetch_by_re(params.build_number_re, content)
    parent_page_id = fetch_by_re(params.parent_page_id_re, content)
    space_key = fetch_by_re(params.space_key_re, content)

    # 350 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("350"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 360 rest/helptips/1.0/tips
    locust.get('/rest/helptips/1.0/tips', catch_response=True)

    # 370 rest/inlinecomments/1.0/comments
    r = locust.get(f'/rest/inlinecomments/1.0/comments'
                   f'?containerId={blog_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)
    content = r.content.decode('utf-8')
    if 'authorDisplayName' not in content and '[]' not in content:
        logger.error(f'Could not open comments for page {blog_id}: {content}')
    assert 'authorDisplayName' in content or '[]' in content, 'Could not open comments for page.'

    # 380 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 390 rest/likes/1.0/content/{blog_id}/likes
    locust.get(f'/rest/likes/1.0/content/{blog_id}/likes'
               f'?commentLikes=true'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 400 rest/highlighting/1.0/panel-items
    locust.get(f'/rest/highlighting/1.0/panel-items'
               f'?pageId={blog_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 410 rest/mywork/latest/status/notification/count
    locust.get(f'/rest/mywork/latest/status/notification/count'
               f'?pageId={blog_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 420 rest/watch-button/1.0/watchState/${ajs-page-id}
    locust.get(f'/rest/watch-button/1.0/watchState/{blog_id}'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 430 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("430"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 440 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("440"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 450 rest/mywork/latest/status/notification/count
    locust.get(f'/rest/mywork/latest/status/notification/count'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 460 /rest/quickreload/latest/{blog_id}
    locust.get(f'/rest/quickreload/latest/{blog_id}'
               f'?since={timestamp_int()}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 470 plugins/editor-loader/editor.action
    r = locust.get(f'/plugins/editor-loader/editor.action'
                   f'?parentPageId={parent_page_id}'
                   f'&pageId={blog_id}'
                   f'&spaceKey={space_key}'
                   f'&atl_after_login_redirect=/pages/viewpage.action'
                   f'&timeout=12000&_={timestamp_int()}',
                   catch_response=True)

    content = r.content.decode('utf-8')
    if 'draftId' not in content:
        logger.error(f'Could not open editor for blog {blog_id}: {content}')
    assert 'draftId' in content, 'Could not open editor for blog.'

    # 480 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("480"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 490 plugins/macrobrowser/browse-macros.action
    locust.get('/plugins/macrobrowser/browse-macros.action'
               '?macroMetadataClientCacheKey=1618473279191'
               '&detailed=false',
               catch_response=True)


def search_cql_and_view_results(locust):
    raise_if_login_failed(locust)

    @confluence_measure('locust_search_cql:recently_viewed')
    def search_recently_viewed():
        # 520 rest/recentlyviewed/1.0/recent
        locust.get('/rest/recentlyviewed/1.0/recent'
                   '?limit=8',
                   catch_response=True)

    @confluence_measure('locust_search_cql:search_results')
    def search_cql():
        # 530 rest/api/search
        r = locust.get(f"/rest/api/search"
                       f"?cql=siteSearch~'{generate_random_string(3, only_letters=True)}'"
                       f"&start=0"
                       f"&limit=20",
                       catch_response=True)

        if '{"results":[' not in r.content.decode('utf-8'):
            logger.locust_info(r.content.decode('utf-8'))
        content = r.content.decode('utf-8')
        if 'results' not in content:
            logger.error(f"Search cql failed: {content}")
        assert 'results' in content, "Search cql failed."

        # 540 rest/mywork/latest/status/notification/count
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

        # 550 pages/createblogpost.action
        r = locust.get(f'/pages/createblogpost.action'
                       f'?spaceKey={blog_space_key}',
                       catch_response=True)

        content = r.content.decode('utf-8')
        if 'Blog post title' not in content:
            logger.error(f'Could not open editor for {blog_space_key}: {content}')
        assert 'Blog post title' in content, 'Could not open editor for blog.'

        content_id = fetch_by_re(params.content_id_re, content)
        parsed_space_key = fetch_by_re(params.space_key, content)
        parsed_page_id = fetch_by_re(params.page_id_re, content)
        parent_page_id = fetch_by_re(params.parent_page_id_re, content)

        # 560 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("560"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 570 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 580 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?pageId={parsed_page_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 590 rest/jiraanywhere/1.0/servers
        locust.get(f'/rest/jiraanywhere/1.0/servers'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 610 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?pageid={parsed_page_id}',
                   catch_response=True)

        # 620 plugins/servlet/notifications-miniview
        locust.get('/plugins/servlet/notifications-miniview', catch_response=True)

        # 630 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "draftType": "blogpost",
                                   "spaceKey": parsed_space_key,
                                   "atl_token": locust.session_data_storage['token']
                                   }

        # 640 json/startheartbeatactivity.action
        r = locust.post('/json/startheartbeatactivity.action',
                        heartbeat_activity_body,
                        TEXT_HEADERS,
                        catch_response=True)

        content = r.content.decode('utf-8')
        if locust.session_data_storage['token'] not in content:
            logger.error(f"Token {locust.session_data_storage['token']} not found in content: {content}")
        assert locust.session_data_storage['token'] in content, 'Token not found in content.'

        contributor_hash = fetch_by_re(params.contribution_hash, content)
        locust.session_data_storage['contributor_hash'] = contributor_hash

        # 650 rest/ui/1.0/content/{content_id}/labels
        r = locust.get(f'/rest/ui/1.0/content/{content_id}/labels', catch_response=True)

        content = r.content.decode('utf-8')
        if '"success":true' not in content:
            logger.error(f'Could not get labels for content {content_id}: {content}')
        assert '"success":true' in content, 'Could not get labels for content in blog editor.'

        draft_name = f"Performance Blog - {generate_random_string(10, only_letters=True)}"
        locust.session_data_storage['draft_name'] = draft_name
        locust.session_data_storage['parsed_space_key'] = parsed_space_key
        locust.session_data_storage['content_id'] = content_id
        locust.session_data_storage['parsed_page_id'] = parsed_page_id
        locust.session_data_storage['parent_page_id'] = parent_page_id

        draft_body = {"draftId": content_id,
                      "pageId": parsed_page_id,
                      "type": "blogpost",
                      "title": draft_name,
                      "spaceKey": parsed_space_key,
                      "content": "<p>test blog draft</p>",
                      "syncRev": "0.mcPCPtDvwoayMR7zvuQSbf8.27"}

        TEXT_HEADERS['Content-Type'] = 'application/json'

        # 660 rest/tinymce/1/drafts
        r = locust.post('/rest/tinymce/1/drafts',
                        json=draft_body,
                        headers=TEXT_HEADERS,
                        catch_response=True)

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

        draft_body = {"status": "current", "title": draft_name, "space": {"key": f"{parsed_space_key}"},
                      "body": {"editor": {"value": f"Test Performance Blog Page Content {draft_name}",
                                          "representation": "editor", "content": {"id": f"{content_id}"}}},
                      "id": f"{content_id}", "type": "blogpost",
                      "version": {"number": 1, "minorEdit": True, "syncRev": "0.mcPCPtDvwoayMR7zvuQSbf8.30"}}
        TEXT_HEADERS['Content-Type'] = 'application/json'

        # 670 rest/api/content/{content_id}?status=draft
        r = locust.client.put(f'/rest/api/content/{content_id}'
                              f'?status=draft',
                              json=draft_body,
                              headers=TEXT_HEADERS,
                              catch_response=True)

        content = r.content.decode('utf-8')
        if 'current' not in content or 'title' not in content:
            logger.error(f'Could not open draft {draft_name}: {content}')
        assert 'current' in content and 'title' in content, 'Could not open blog draft.'
        created_blog_title = fetch_by_re(params.created_blog_title_re, content)
        logger.locust_info(f'Blog {created_blog_title} created')

        # 680 {created_blog_title}
        r = locust.get(f'/{created_blog_title}', catch_response=True)

        content = r.content.decode('utf-8')
        if 'Created by' not in content:
            logger.error(f'Could not open created blog {created_blog_title}: {content}')
        assert 'Created by' in content, 'Could not open created blog.'

        heartbeat_activity_body = {"dataType": "json",
                                   "contentId": content_id,
                                   "draftType": "blogpost",
                                   "spaceKey": parsed_space_key,

                                   "atl_token": locust.session_data_storage['token']
                                   }

        # 690 json/stopheartbeatactivity.action
        r = locust.post('/json/startheartbeatactivity.action',
                        heartbeat_activity_body,
                        TEXT_HEADERS,
                        catch_response=True)

        # 700 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("700"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 710 plugins/servlet/notifications-miniview
        locust.get('/plugins/servlet/notifications-miniview', catch_response=True)

        # 720 rest/watch-button/1.0/watchState/{content-id}
        locust.get(f'/rest/watch-button/1.0/watchState/{content_id}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 730 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("730"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 740 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("740"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 750 /rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 760 rest/jira-metadata/1.0/metadata/aggregate
        locust.get(f'/rest/jira-metadata/1.0/metadata/aggregate'
                   f'?pageId={locust.session_data_storage["parsed_page_id"]}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 770 rest/likes/1.0/content/{content_id}/likes
        locust.get(f'/rest/likes/1.0/content/{content_id}/likes'
                   f'?commentLikes=true'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 780 rest/highlighting/1.0/panel-items
        locust.get(f'/rest/highlighting/1.0/panel-items'
                   f'?pageId={content_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 790 rest/inlinecomments/1.0/comments
        locust.get(f'/rest/inlinecomments/1.0/comments'
                   f'?containerId={content_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 800 s/en_GB/{build-number}/{keyboardshortcut-hash}/_/images/icons/profilepics/add_profile_pic.svg
        locust.get(f'/s/en_GB/{build_number}/{keyboard_hash}/_/images/icons/profilepics/add_profile_pic.svg',
                   catch_response=True)

        # 810 rest/helptips/1.0/tips
        locust.get('/rest/helptips/1.0/tips', catch_response=True)

        # 820 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?pageid={content_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 830 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("830"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 840 rest/autoconvert/latest/shortcutlinkconfigurations
        locust.get(f'/rest/autoconvert/latest/shortcutlinkconfigurations'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 850 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("850"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 880 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("880"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 890 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("890"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 900 plugins/editor-loader/editor.action
        r = locust.get(f'/plugins/editor-loader/editor.action'
                       f'?parentPageId={locust.session_data_storage["parent_page_id"]}'
                       f'&pageId={content_id}'
                       f'&spaceKey={parsed_space_key}'
                       f'&atl_after_login_redirect=/pages/viewpage.action'
                       f'&timeout=12000&_={timestamp_int()}',
                       catch_response=True)

        # 910 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("830"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 920 json/startheartbeatactivity.action
        r = locust.post('/json/startheartbeatactivity.action',
                        heartbeat_activity_body,
                        TEXT_HEADERS,
                        catch_response=True)

        content = r.content.decode('utf-8')
        if locust.session_data_storage['token'] not in content:
            logger.error(f"Token {locust.session_data_storage['token']} not found in content: {content}")
        assert locust.session_data_storage['token'] in content, 'Token not found in content.'

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

        # 960 pages/createpage.action
        r = locust.get(f'/pages/createpage.action'
                       f'?spaceKey={space_key}'
                       f'&fromPageId={page_id}'
                       f'&src=quick-create',
                       catch_response=True)

        content = r.content.decode('utf-8')
        if 'Page Title' not in content:
            logger.error(f'Could not open page editor: {content}')
        assert 'Page Title' in content, 'Could not open page editor.'

        content_id_fetched_by_re = fetch_by_re(params.content_id_re, content)
        parent_page_id_fetched_by_re = fetch_by_re(params.parent_page_id, content)

        # 970 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("970"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 980 rest/create-dialog/1.0/storage/quick-create
        locust.get('/rest/create-dialog/1.0/storage/quick-create', catch_response=True)

        # 990 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1000 plugins/macrobrowser/browse-macros.action
        locust.get(f'/plugins/macrobrowser/browse-macros.action'
                   f'?macroMetadataClientCacheKey={timestamp_int()}'
                   f'&detailed=false',
                   catch_response=True)

        # 1010 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?pageid=0'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1030 rest/jiraanywhere/1.0/servers
        locust.get(f'/rest/jiraanywhere/1.0/servers'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        start_heartbeat_activity_body = {"dataType": "json",
                                         "contentId": content_id_fetched_by_re,
                                         "draftType": "page",
                                         "spaceKey": space_key,
                                         "atl_token": locust.session_data_storage['token']
                                         }

        # 1040 json/startheartbeatactivity.action
        r = locust.post('/json/startheartbeatactivity.action',
                        start_heartbeat_activity_body,
                        TEXT_HEADERS,
                        catch_response=True)

        contributor_hash = r.json().get("contributorsHash", None)
        if contributor_hash is None:
            logger.error(f'The "contributorsHash" key was not found in content: {r.json()}')
        assert contributor_hash is not None, 'The "contributorsHash" key was not found in content.'

        # 1050 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1080 rest/autoconvert/latest/shortcutlinkconfigurations
        locust.get(f'/rest/autoconvert/latest/shortcutlinkconfigurations'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1090 rest/ui/1.0/content/{content_id}/labels
        locust.get(f'/rest/ui/1.0/content/{content_id_fetched_by_re}/labels'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1100 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1100"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1110 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1110"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1120 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1120"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        locust.session_data_storage["content_id"] = content_id_fetched_by_re
        locust.session_data_storage["parent_page_id"] = parent_page_id_fetched_by_re
        locust.session_data_storage["contributor_hash"] = contributor_hash

    @confluence_measure('locust_create_and_edit_page:create_page')
    def create_page():
        raise_if_login_failed(locust)
        draft_name = f"{generate_random_string(10, only_letters=True)}"
        title = f"locust_create_and_edit_page:create_page - {draft_name}"
        body_editor_value = f"Test Performance Create Page Content {draft_name}"

        create_page_body_data = {"status": "current",
                                 "title": title,
                                 "space": {
                                     "key": space_key
                                 },
                                 "body": {
                                     "editor": {
                                         "value": body_editor_value,
                                         "representation": "editor",
                                         "content": {
                                             "id": locust.session_data_storage['content_id']
                                         }
                                     }
                                 },
                                 "id": locust.session_data_storage['content_id'],
                                 "type": "page",
                                 "version": {
                                     "number": 1,
                                     "minorEdit": "true",
                                     "syncRev": "0.RIi4Ras2AToROk0WlzfpzBg.2"
                                 },
                                 "ancestors": [
                                     {
                                         "id": locust.session_data_storage['parent_page_id'],
                                         "type": "page"
                                     }
                                 ]
                                 }

        TEXT_HEADERS['Content-Type'] = 'application/json'
        TEXT_HEADERS['X-Requested-With'] = 'XMLHttpRequest'

        start_heartbeat_activity_body = {"dataType": "json",
                                         "contentId": locust.session_data_storage["content_id"],
                                         "space_key": space_key,
                                         "draftType": "page",
                                         "atl_token": locust.session_data_storage['token'],
                                         "contributorsHash": locust.session_data_storage['contributor_hash'],
                                         }

        stop_heartbeat_activity_body = {"dataType": "json",
                                        "contentId": locust.session_data_storage["content_id"],
                                        "draftType": "page",
                                        "atl_token": locust.session_data_storage['token'],
                                        }

        # 1130 json/startheartbeatactivity.action
        locust.post('/json/startheartbeatactivity.action',
                    params=start_heartbeat_activity_body,
                    headers=TEXT_HEADERS,
                    catch_response=True)

        # 1140 rest/api/content/content_id?status=draft
        r = locust.client.put(f'/rest/api/content/{locust.session_data_storage["content_id"]}'
                              f'?status=draft',
                              json=create_page_body_data,
                              headers=TEXT_HEADERS,
                              catch_response=True)

        content = r.json()
        page_title = content.get('title', None)

        if page_title is None:
            logger.error(f'Could not create PAGE draft: {content}')
        assert page_title is not None, 'Could not create PAGE draft.'

        locust.session_data_storage['draft_name'] = draft_name

        # 1045 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?_{timestamp_int()}',
                   catch_response=True)

        # 1150 json/stopheartbeatactivity.action
        locust.post('/json/stopheartbeatactivity.action',
                    params=stop_heartbeat_activity_body,
                    headers=TEXT_HEADERS,
                    catch_response=True)

        # 1160 display/{space_key}/{page_title}
        locust.get(f'/display/{space_key}/{page_title}', catch_response=True)

        # 1170 json/startheartbeatactivity.action
        locust.post('/json/startheartbeatactivity.action',
                    params=start_heartbeat_activity_body,
                    headers=TEXT_HEADERS,
                    catch_response=True)

        # 1180 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1180"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1190 rest/helptips/1.0/tips
        locust.get('/rest/helptips/1.0/tips', catch_response=True)

        # 1200 rest/inlinecomments/1.0/comments
        locust.get(f'/rest/inlinecomments/1.0/comments'
                   f'?containerId={locust.session_data_storage["content_id"]}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1210 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1220 plugins/pagetree/naturalchildren.action
        locust.get(f'/plugins/pagetree/naturalchildren.action'
                   f'?decorator=none'
                   f'&expandCurrent=true'
                   f'&mobile=false'
                   f'&sort=position'
                   f'&reverse=false'
                   f'&spaceKey={space_key}'
                   f'&treeId=0'
                   f'&hasRoot=false'
                   f'&startDepth=0'
                   f'&disableLinks=false'
                   f'&placement=sidebar'
                   f'&excerpt=false'
                   f'&ancestors={locust.session_data_storage["parent_page_id"]}'
                   f'&treePageId=0'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1230 rest/jira-metadata/1.0/metadata/aggregate
        locust.get(f'/rest/jira-metadata/1.0/metadata/aggregate'
                   f'?pageId=0'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1240 rest/likes/1.0/content/{content_id}/likes
        locust.get(f'/rest/likes/1.0/content/{locust.session_data_storage["content_id"]}/likes'
                   f'?commentLikes=true'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1250 rest/highlighting/1.0/panel-items
        locust.get(f'/rest/highlighting/1.0/panel-items'
                   f'?pageId=0'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1260 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?pageid=0'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1270 rest/watch-button/1.0/watchState/{content_id}
        locust.get(f'/rest/watch-button/1.0/watchState/{locust.session_data_storage["content_id"]}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1280 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1280"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1290 plugins/editor-loader/editor.action
        r = locust.get(f'/plugins/editor-loader/editor.action'
                       f'?parentPageId={locust.session_data_storage["parent_page_id"]}'
                       f'&pageId={locust.session_data_storage["content_id"]}'
                       f'&spaceKey={space_key}'
                       f'&atl_after_login_redirect=/display/{space_key}/{page_title}'
                       f'&timeout=12000&_={timestamp_int()}',
                       catch_response=True)

        content = r.content.decode('utf-8')
        if page_title not in content:
            logger.error(f'{page_title}: {content}')
        assert page_title in content, 'Page editor load failed for page.'

        # 1300 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1300"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1310 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1310"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1320 plugins/macrobrowser/browse-macros.action
        locust.get('/plugins/macrobrowser/browse-macros.action'
                   '?macroMetadataClientCacheKey=1618492783694'
                   '&detailed=false',
                   catch_response=True)

    @confluence_measure('locust_create_and_edit_page:open_editor')
    def open_editor():
        raise_if_login_failed(locust)
        start_heartbeat_activity_body = {"dataType": "json",
                                         "contentId": locust.session_data_storage["content_id"],
                                         "space_key": space_key,
                                         "draftType": "page",
                                         "atl_token": locust.session_data_storage['token'],
                                         }

        # 1360 rest/tinymce/1/content/{content_id}.json
        locust.get(f'/rest/tinymce/1/content/{locust.session_data_storage["content_id"]}.json'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1370 rest/jiraanywhere/1.0/servers
        locust.get(f'/rest/jiraanywhere/1.0/servers'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1380 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1390 json/startheartbeatactivity.action
        locust.post('/json/startheartbeatactivity.action',
                    params=start_heartbeat_activity_body,
                    headers=TEXT_HEADERS,
                    catch_response=True)

        # 1400 rest/api/content/{content_id}
        locust.get(f'/rest/api/content/{locust.session_data_storage["content_id"]}'
                   f'?expand=history.createdBy.status,history.contributors.publishers.users.status,'
                   f'children.comment.version.by.status'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1410 rest/autoconvert/latest/shortcutlinkconfigurations
        locust.get(f'/rest/autoconvert/latest/shortcutlinkconfigurations'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1420 rest/autoconvert/latest/shortcutlinkconfigurations
        locust.get(f'/rest/ui/1.0/content/{locust.session_data_storage["content_id"]}/labels'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1430 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1430"),
                    headers=TEXT_HEADERS,
                    catch_response=True)

        # 1440 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1450 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1450"),
                    headers=TEXT_HEADERS,
                    catch_response=True)

    @confluence_measure('locust_create_and_edit_page:edit_page')
    def edit_page():
        raise_if_login_failed(locust)
        locust.session_data_storage['draft_name'] = f"{generate_random_string(10, only_letters=True)}"
        title = f"locust_create_and_edit_page:edit_page - {locust.session_data_storage['draft_name']}"
        body_editor_value = f"<p>Page edit with locust {locust.session_data_storage['draft_name']}</p>"

        TEXT_HEADERS['Content-Type'] = 'application/json'
        TEXT_HEADERS['X-Requested-With'] = 'XMLHttpRequest'

        start_heartbeat_activity_body = {"dataType": "json",
                                         "contentId": locust.session_data_storage["content_id"],
                                         "space_key": space_key,
                                         "draftType": "page",
                                         "atl_token": locust.session_data_storage['token'],
                                         "contributorsHash": locust.session_data_storage['contributor_hash'],
                                         }

        stop_heartbeat_activity_body = {"dataType": "json",
                                        "contentId": locust.session_data_storage["content_id"],
                                        "draftType": "page",
                                        "atl_token": locust.session_data_storage['token'],
                                        }

        edt_page_body_data = {"status": "current",
                              "title": title,
                              "space": {
                                  "key": space_key
                              },
                              "body": {
                                  "editor": {
                                      "value": body_editor_value,
                                      "representation": "editor",
                                      "content": {
                                          "id": locust.session_data_storage['content_id']
                                      }
                                  }
                              },
                              "id": locust.session_data_storage['content_id'],
                              "type": "page",
                              "version": {
                                  "number": 2,
                                  "message": "",
                                  "minorEdit": "false",
                                  "syncRev": "0.oLWs6S5l3gY2mwHJiA9jHao.5"
                              },
                              "ancestors": [
                                  {
                                      "id": locust.session_data_storage['parent_page_id'],
                                      "type": "page"
                                  }
                              ]
                              }

        # 1460 json/startheartbeatactivity.action
        locust.post('/json/startheartbeatactivity.action',
                    params=start_heartbeat_activity_body,
                    headers=TEXT_HEADERS,
                    catch_response=True)

        # 1470 rest/api/content/{content_id}?status=draft
        r = locust.client.put(f'/rest/api/content/{locust.session_data_storage["content_id"]}'
                              f'?status=draft',
                              json=edt_page_body_data,
                              headers=TEXT_HEADERS,
                              catch_response=True)

        content = r.json()
        page_title = content.get('title', None)

        if page_title is None:
            logger.info(f'Could not edit page. Response content: {content}')
            logger.error(f'User {locust.session_data_storage["username"]} could not edit page '
                         f'{locust.session_data_storage["content_id"]}, '
                         f'parent page id: {locust.session_data_storage["parent_page_id"]}: {content}')
        assert page_title is not None, 'User could not edit page.'

        # 1480 json/stopheartbeatactivity.action
        locust.post('/json/stopheartbeatactivity.action',
                    params=stop_heartbeat_activity_body,
                    headers=TEXT_HEADERS,
                    catch_response=True)

        # 1490 /display/${space_key}/${page_title}
        locust.get(f'/display/{space_key}/{page_title}',
                   catch_response=True)

        # 1500 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1500"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1510 rest/helptips/1.0/tips
        locust.get('/rest/helptips/1.0/tips', catch_response=True)

        locust.get(f'/rest/inlinecomments/1.0/comments'
                   f'?containerId={locust.session_data_storage["content_id"]}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1530 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
        locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1540 plugins/pagetree/naturalchildren.action
        locust.get(f'/plugins/pagetree/naturalchildren.action'
                   f'?decorator=none'
                   f'&expandCurrent=true'
                   f'&mobile=false'
                   f'&sort=position'
                   f'&reverse=false'
                   f'&spaceKey={space_key}'
                   f'&treeId=0'
                   f'&hasRoot=false'
                   f'&startDepth=0'
                   f'&disableLinks=false'
                   f'&placement=sidebar'
                   f'&excerpt=false'
                   f'&ancestors={locust.session_data_storage["parent_page_id"]}'
                   f'&treePageId={space_key}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1550 rest/jira-metadata/1.0/metadata/aggregate
        locust.get(f'/rest/jira-metadata/1.0/metadata/aggregate'
                   f'?pageId={page_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1560 rest/likes/1.0/content/{content_id}/likes
        locust.get(f'/rest/likes/1.0/content/{locust.session_data_storage["content_id"]}/likes'
                   f'?commentLikes=true'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1570 rest/highlighting/1.0/panel-items
        locust.get(f'/rest/highlighting/1.0/panel-items'
                   f'?pageId={page_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1580 rest/mywork/latest/status/notification/count
        locust.get(f'/rest/mywork/latest/status/notification/count'
                   f'?pageid={page_id}'
                   f'&_={timestamp_int()}', catch_response=True)

        # 1590 rest/watch-button/1.0/watchState/{content_id}
        locust.get(f'/rest/watch-button/1.0/watchState/{locust.session_data_storage["content_id"]}'
                   f'?_={timestamp_int()}',
                   catch_response=True)

        # 1600 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1600"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1610 plugins/editor-loader/editor.action
        locust.get(f'/plugins/editor-loader/editor.action?parent'
                   f'parentPageId={locust.session_data_storage["parent_page_id"]}'
                   f'&pageId={locust.session_data_storage["content_id"]}'
                   f'&spaceKey={space_key}'
                   f'&atl_after_login_redirect=/pages/viewpage.action'
                   f'&timeout=12000'
                   f'&_={timestamp_int()}', catch_response=True)

        # 1620 rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1620"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1630 rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1630"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1640 plugins/macrobrowser/browse-macros.action
        locust.get('/plugins/macrobrowser/browse-macros.action'
                   '?macroMetadataClientCacheKey=1618492783694'
                   '&detailed=false',
                   catch_response=True)

    create_page_editor()
    create_page()
    open_editor()
    edit_page()


@confluence_measure('locust_comment_page')
def comment_page(locust):
    params = CommentPage()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]
    space_key = page[1]
    comment_text = generate_random_string(length=15, only_letters=True)
    comment = f'<div style="display: none;"><br /></div><p>{comment_text}</p>'
    uid = str(uuid.uuid4())
    build_number = locust.session_data_storage.get('build_number', '')
    keyboard_hash = locust.session_data_storage.get('keyboard_hash', '')

    start_heartbeat_activity_body = {"dataType": "json",
                                     "contentId": page_id,
                                     "space_key": space_key,
                                     "draftType": "comment",
                                     "atl_token": locust.session_data_storage['token'],
                                     }

    # 1680 rest/jiraanywhere/1.0/servers
    locust.get(f'/rest/jiraanywhere/1.0/servers'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 1690 /rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 1700 json/startheartbeatactivity.action
    locust.post('/json/startheartbeatactivity.action',
                params=start_heartbeat_activity_body,
                headers=TEXT_HEADERS,
                catch_response=True)

    # 1710 rest/autoconvert/latest/shortcutlinkconfigurations
    locust.get(f'/rest/autoconvert/latest/shortcutlinkconfigurations'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 1720 rest/mywork/latest/status/notification/count
    locust.get(f'/rest/mywork/latest/status/notification/count'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 1730 rest/tinymce/1/content/{page_id}/comment
    r = locust.post(f'/rest/tinymce/1/content/{page_id}/comment'
                    f'?actions=true',
                    params={'html': comment, 'watch': True, 'uuid': uid},
                    headers=NO_TOKEN_HEADERS,
                    catch_response=True)

    content = r.content.decode('utf-8')
    if comment_text not in content:
        logger.error(f'Could not add comment: {content}')
    assert comment_text in content, 'Could not add comment.'

    # 1740 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("1740"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


@confluence_measure('locust_view_attachment')
def view_attachments(locust):
    raise_if_login_failed(locust)

    params = ViewAttachment()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]
    space_key = page[1]

    # 1750 rest/quickreload/latest/{page_id}
    locust.get(f'/rest/quickreload/latest/{page_id}'
               f'?since={timestamp_int()}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 1760 pages/viewpageattachments.action
    r = locust.get(f'/pages/viewpageattachments.action'
                   f'?pageId={page_id}',
                   catch_response=True)

    content = r.content.decode('utf-8')

    if not ('Upload file' in content and 'Attach more files' in content or 'currently no attachments' in content):
        logger.error(f'View attachments failed: {content}')
    assert 'Upload file' in content and 'Attach more files' in content \
           or 'currently no attachments' in content, 'View attachments failed.'
    build_number = fetch_by_re(params.build_number_re, content)
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    parent_page_id = fetch_by_re(params.parent_page_id_re, content)

    # 1770 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 1790 rest/mywork/latest/status/notification/count
    locust.get(f'/rest/mywork/latest/status/notification/count'
               f'?pageid={page_id}'
               f'&_={timestamp_int()}', catch_response=True)

    # 1800 plugins/pagetree/naturalchildren.action
    locust.get(f'/plugins/pagetree/naturalchildren.action'
               f'?decorator=none'
               f'&expandCurrent=true'
               f'&mobile=false'
               f'&sort=position'
               f'&reverse=false'
               f'&spaceKey={space_key}'
               f'&treeId=0'
               f'&hasRoot=false'
               f'&startDepth=0'
               f'&disableLinks=false'
               f'&placement=sidebar'
               f'&excerpt=false'
               f'&ancestors={parent_page_id}'
               f'&treePageId={page_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 1810 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1810"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1820 plugins/editor-loader/editor.action
    locust.get(f'/plugins/editor-loader/editor.action?parent'
               f'parentPageId={parent_page_id}'
               f'&pageId={page_id}'
               f'&spaceKey={space_key}'
               f'&atl_after_login_redirect=/pages/viewpage.action'
               f'&timeout=12000'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 1830 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("1830"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1840 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1840"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1850 plugins/macrobrowser/browse-macros.action
    locust.get('/plugins/macrobrowser/browse-macros.action'
               '?macroMetadataClientCacheKey=1618579820365'
               '&detailed=false',
               catch_response=True)

    # 1890 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1890"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


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
    space_key = page[1]

    r = locust.get(f'/pages/viewpage.action?pageId={page_id}', catch_response=True)
    content = r.content.decode('utf-8')
    if not('Created by' in content and 'Save for later' in content):
        logger.error(f'Failed to open page {page_id}: {content}')
    assert 'Created by' in content and 'Save for later' in content, 'Failed to open page to upload attachments.'
    build_number = fetch_by_re(params.build_number_re, content)
    keyboard_hash = fetch_by_re(params.keyboard_hash_re, content)
    parent_page_id = fetch_by_re(params.parent_page_id_re, content)

    multipart_form_data = {
        "file": (file_name, open(file_path, 'rb'), file_extension)
    }

    # 1900 pages/doattachfile.action?pageId={page_id}
    r = locust.post(f'/pages/doattachfile.action'
                    f'?pageId={page_id}',
                    params={"atl_token": locust.session_data_storage['token'], "comment_0": "", "comment_1": "",
                            "comment_2": "", "comment_3": "", "comment_4": "0", "confirm": "Attach"},
                    files=multipart_form_data,
                    catch_response=True)
    content = r.content.decode('utf-8')
    if not('Upload file' in content and 'Attach more files' in content):
        logger.error(f'Could not upload attachments: {content}')
    assert 'Upload file' in content and 'Attach more files' in content, 'Could not upload attachments.'

    # 1910 rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}
    locust.get(f'/rest/shortcuts/latest/shortcuts/{build_number}/{keyboard_hash}'
               f'?_={timestamp_int()}',
               catch_response=True)

    # 1920 plugins/pagetree/naturalchildren.action
    locust.get(f'/plugins/pagetree/naturalchildren.action'
               f'?decorator=none'
               f'&expandCurrent=true'
               f'&mobile=false'
               f'&sort=position'
               f'&reverse=false'
               f'&spaceKey={space_key}'
               f'&treeId=0'
               f'&hasRoot=false'
               f'&startDepth=0'
               f'&disableLinks=false'
               f'&placement=sidebar'
               f'&excerpt=false'
               f'&ancestors={parent_page_id}'
               f'&treePageId={page_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 1930 rest/mywork/latest/status/notification/count
    locust.get(f'/rest/mywork/latest/status/notification/count'
               f'?pageid={page_id}'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 1940 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1940"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1950 rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("1950"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1960 plugins/editor-loader/editor.action
    locust.get(f'/plugins/editor-loader/editor.action?parent'
               f'parentPageId={parent_page_id}'
               f'&pageId={page_id}'
               f'&spaceKey={space_key}'
               f'&atl_after_login_redirect=/pages/viewpage.action'
               f'&timeout=12000'
               f'&_={timestamp_int()}',
               catch_response=True)

    # 1970 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1970"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1980 plugins/macrobrowser/browse-macros.action
    locust.get('/plugins/macrobrowser/browse-macros.action'
               '?macroMetadataClientCacheKey=1618624163503'
               '&detailed=false',
               catch_response=True)

    # 1990 rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1990"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


@confluence_measure('locust_like_page')
def like_page(locust):
    raise_if_login_failed(locust)
    params = LikePage()
    page = random.choice(confluence_dataset["pages"])
    page_id = page[0]

    JSON_HEADERS['Origin'] = CONFLUENCE_SETTINGS.server_url

    # 2030 rest/likes/1.0/content/{page_id}/likes
    r = locust.get(f'/rest/likes/1.0/content/{page_id}/likes',
                   headers=JSON_HEADERS,
                   catch_response=True)

    content = r.content.decode('utf-8')
    like = fetch_by_re(params.like_re, content)

    if like is None:
        # 2050 rest/likes/1.0/content/{page_id}/likes
        r = locust.post(f'/rest/likes/1.0/content/{page_id}/likes',
                        headers=JSON_HEADERS,
                        catch_response=True)
    else:
        # 2040 rest/likes/1.0/content/${page_id}/likes
        r = locust.client.delete(f'/rest/likes/1.0/content/{page_id}/likes',
                                 catch_response=True)

    content = r.content.decode('utf-8')
    if 'likes' not in content:
        logger.error(f"Could not set like to the page {page_id}: {content}")
    assert 'likes' in r.content.decode('utf-8'), 'Could not set like to the page.'
