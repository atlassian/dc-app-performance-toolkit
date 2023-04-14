import random
import re
from locustio.jira.requests_params import Login, BrowseIssue, CreateIssue, SearchJql, ViewBoard, BrowseBoards, \
    BrowseProjects, AddComment, ViewDashboard, EditIssue, ViewProjectSummary, jira_datasets
from locustio.common_utils import jira_measure, fetch_by_re, timestamp_int, generate_random_string, TEXT_HEADERS, \
    ADMIN_HEADERS, NO_TOKEN_HEADERS, RESOURCE_HEADERS, init_logger, raise_if_login_failed

from util.conf import JIRA_SETTINGS
import uuid

logger = init_logger(app_type='jira')
jira_dataset = jira_datasets()


@jira_measure('locust_login_and_view_dashboard')
def login_and_view_dashboard(locust):
    session_id = str(uuid.uuid4())
    locust.cross_action_storage[session_id] = dict()
    locust.session_data_storage = locust.cross_action_storage[session_id]
    locust.session_data_storage['app'] = 'jira'

    params = Login()

    user = random.choice(jira_dataset["users"])
    body = params.login_body
    body['os_username'] = user[0]
    body['os_password'] = user[1]

    # 100 /login.jsp
    locust.post('/login.jsp', body,
                TEXT_HEADERS,
                catch_response=True)

    r = locust.get('/', catch_response=True)
    if not r.content:
        raise Exception('Please check server hostname in jira.yml file')
    content = r.content.decode('utf-8')

    # 110 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("110"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 115 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("115"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 120 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("120"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 125 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("125"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 130 /plugins/servlet/gadgets/dashboard-diagnostics
    locust.post("/plugins/servlet/gadgets/dashboard-diagnostics",
                {"uri": f"{locust.client.base_url.lower()}/secure/Dashboard.jspa"},
                TEXT_HEADERS,
                catch_response=True)

    # 135 /rest/activity-stream/1.0/preferences
    locust.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)

    # 140 /rest/gadget/1.0/issueTable/jql
    locust.get(f'/rest/gadget/1.0/issueTable/jql?num=10&tableContext=jira.table.cols.dashboard'
               f'&addDefault=true&enableSorting=true&paging=true&showActions=true'
               f'&jql=assignee+%3D+currentUser()+AND'
               f'+resolution+%3D+unresolved+ORDER+BY+priority+DESC%2C+created+ASC'
               f'&sortBy=&startIndex=0&_={timestamp_int()}', catch_response=True)

    # 145 /plugins/servlet/streams
    locust.get(f'/plugins/servlet/streams?maxResults=5&relativeLinks=true&_={timestamp_int()}', catch_response=True)

    # Assertions
    token = fetch_by_re(params.atl_token_pattern, content)
    if not (f'title="loggedInUser" value="{user[0]}">' in content):
        logger.error(f'User {user[0]} authentication failed: {content}')
    assert f'title="loggedInUser" value="{user[0]}">' in content, 'User authentication failed'

    locust.session_data_storage['username'] = user[0]
    locust.session_data_storage['password'] = user[1]
    locust.session_data_storage["token"] = token
    logger.locust_info(f"{params.action_name}: User {user[0]} logged in with atl_token: {token}")


@jira_measure('locust_view_issue')
def view_issue(locust):
    raise_if_login_failed(locust)
    params = BrowseIssue()
    issue_key = random.choice(jira_dataset['issues'])[0]
    project_key = random.choice(jira_dataset['issues'])[2]

    # 400 /browse
    r = locust.get(f'/browse/{issue_key}', catch_response=True)

    content = r.content.decode('utf-8')
    issue_id = fetch_by_re(params.issue_id_pattern, content)
    project_avatar_id = fetch_by_re(params.project_avatar_id_pattern, content)
    edit_allowed = fetch_by_re(params.edit_allow_pattern, content, group_no=0)

    # 405 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("405"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 410 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("410"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 415 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("415"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 420 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("420"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 425 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("425"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 430 /secure/projectavatar
    locust.get(f'/secure/projectavatar?avatarId={project_avatar_id}', catch_response=True)

    # Assertions
    if not (f'<meta name="ajs-issue-key" content="{issue_key}">' in content):
        logger.error(f'Issue {issue_key} not found: {content}')
    assert f'<meta name="ajs-issue-key" content="{issue_key}">' in content, 'Issue not found'
    logger.locust_info(f"{params.action_name}: Issue {issue_key} is opened successfully")
    logger.locust_info(f'{params.action_name}: Issue key - {issue_key}, issue_id - {issue_id}')

    # 435 /secure/AjaxIssueEditAction!default.jspa
    if edit_allowed:
        url = f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId={issue_id}&_={timestamp_int()}'
        locust.get(url, catch_response=True)

    # 440 /rest/projects/1.0/project/<project_key>/lastVisited
    locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                      params.browse_project_payload,
                      catch_response=True)


def create_issue(locust):
    params = CreateIssue()
    project = random.choice(jira_dataset['projects'])
    project_id = project[1]

    @jira_measure('locust_create_issue:open_quick_create')
    def create_issue_open_quick_create():
        raise_if_login_failed(locust)

        # 200 /secure/QuickCreateIssue!default.jspa?decorator=none
        r = locust.post(f'/secure/QuickCreateIssue!default.jspa?',
                        json={'atl_token': locust.session_data_storage["token"]},
                        headers=ADMIN_HEADERS, catch_response=True)

        content = r.content.decode('utf-8')
        atl_token = fetch_by_re(params.atl_token_pattern, content)
        form_token = fetch_by_re(params.form_token_pattern, content)
        issue_type = fetch_by_re(params.issue_type_pattern, content)
        resolution_done = fetch_by_re(params.resolution_done_pattern, content)
        fields_to_retain = re.findall(params.fields_to_retain_pattern, content)
        custom_fields_to_retain = re.findall(params.custom_fields_to_retain_pattern, content)

        issue_body_params_dict = {'atl_token': atl_token,
                                  'form_token': form_token,
                                  'issue_type': issue_type,
                                  'project_id': project_id,
                                  'resolution_done': resolution_done,
                                  'fields_to_retain': fields_to_retain,
                                  'custom_fields_to_retain': custom_fields_to_retain
                                  }

        if not ('"id":"project","label":"Project"' in content):
            logger.error(f'{params.err_message_create_issue}: {content}')
        assert '"id":"project","label":"Project"' in content, params.err_message_create_issue

        # 205 /rest/quickedit/1.0/userpreferences/create
        locust.post('/rest/quickedit/1.0/userpreferences/create',
                    json=params.user_preferences_payload,
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 210 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("210"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        locust.session_data_storage['issue_body_params_dict'] = issue_body_params_dict

    create_issue_open_quick_create()

    @jira_measure('locust_create_issue:fill_and_submit_issue_form')
    def create_issue_submit_form():
        raise_if_login_failed(locust)
        issue_body = params.prepare_issue_body(locust.session_data_storage['issue_body_params_dict'],
                                               user=locust.session_data_storage["username"])

        # 215 /secure/QuickCreateIssue.jspa?decorator=none
        r = locust.post('/secure/QuickCreateIssue.jspa?decorator=none',
                        params=issue_body,
                        headers=ADMIN_HEADERS,
                        catch_response=True)

        # 220 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("220"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        content = r.content.decode('utf-8')
        if '"id":"project","label":"Project"' not in content:
            logger.error(f'{params.err_message_create_issue}: {content}')
        assert '"id":"project","label":"Project"' in content, params.err_message_create_issue
        issue_key = fetch_by_re(params.create_issue_key_pattern, content)
        logger.locust_info(f"{params.action_name}: Issue {issue_key} was successfully created")

    create_issue_submit_form()


@jira_measure('locust_search_jql')
def search_jql(locust):
    raise_if_login_failed(locust)
    params = SearchJql()
    jql = random.choice(jira_dataset['jqls'])[0]

    # 300 /issues
    locust.get(f'/issues/?jql={jql}', catch_response=True)

    # 305 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("305"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 310 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("310"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 315 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("315"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 320 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("320"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 325 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("325"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 330 /rest/api/2/filter/favourite
    locust.get(f'/rest/api/2/filter/favourite?expand=subscriptions[-5:]&_={timestamp_int()}',
               catch_response=True)

    # 335 /rest/issueNav/latest/preferredSearchLayout
    locust.post('/rest/issueNav/latest/preferredSearchLayout',
                params={'layoutKey': 'split-view'},
                headers=NO_TOKEN_HEADERS,
                catch_response=True)

    # 340 /rest/issueNav/1/issueTable
    r = locust.post('/rest/issueNav/1/issueTable',
                    data=params.issue_table_payload,
                    headers=NO_TOKEN_HEADERS,
                    catch_response=True)

    content = r.content.decode('utf-8')
    issue_ids = re.findall(params.ids_pattern, content)

    if issue_ids:
        body = params.prepare_jql_body(issue_ids)

        # 345 /rest/issueNav/1/issueTable/stable
        r = locust.post('/rest/issueNav/1/issueTable/stable',
                        data=body,
                        headers=NO_TOKEN_HEADERS,
                        catch_response=True)

        content = r.content.decode('utf-8')
        issue_key = fetch_by_re(params.issue_key_pattern, content)
        issue_id = fetch_by_re(params.issue_id_pattern, content)

    # 350 /secure/QueryComponent!Jql.jspa
    locust.post('/secure/QueryComponent!Jql.jspa',
                params={'jql': 'order by created DESC', 'decorator': None},
                headers=TEXT_HEADERS,
                catch_response=True)

    # 355 /rest/orderbycomponent/latest/orderByOptions/primary
    locust.post('/rest/orderbycomponent/latest/orderByOptions/primary',
                json={"jql": "order by created DESC"},
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 360 /secure/AjaxIssueAction!default.jspa
    if issue_ids:
        r = locust.post('/secure/AjaxIssueAction!default.jspa',
                        params={"decorator": None,
                                "issueKey": issue_key,
                                "prefetch": False,
                                "shouldUpdateCurrentProject": False,
                                "loadFields": False,
                                "_": timestamp_int()},
                        headers=TEXT_HEADERS,
                        catch_response=True)

        # 365 /secure/AjaxIssueEditAction!default.jspa
        if params.edit_allow_string in r.content.decode('utf-8'):
            locust.get(f'/secure/AjaxIssueEditAction!default.jspa?'
                       f'decorator=none&issueId={issue_id}&_={timestamp_int()}', catch_response=True)


@jira_measure('locust_view_project_summary')
def view_project_summary(locust):
    raise_if_login_failed(locust)
    params = ViewProjectSummary()
    project = random.choice(jira_dataset['projects'])
    project_key = project[0]

    # 500 /projects/<project_key>/summary
    r = locust.get(f'/projects/{project_key}/summary', catch_response=True)

    content = r.content.decode('utf-8')
    logger.locust_info(f"{params.action_name}. View project {project_key}: {content}")

    assert_string = f'["project-key"]="\\"{project_key}\\"'
    if not (assert_string in content):
        logger.error(f'{params.err_message} {project_key}')
    assert assert_string in content, params.err_message

    # 505 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("505"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 510 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("510"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 515 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("515"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 520 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("520"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 525 /rest/activity-stream/1.0/preferences
    locust.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)

    # 530 /projects/<project_key>
    locust.get(f'/projects/{project_key}?selectedItem=com.atlassian.jira.jira-projects-plugin:'
               f'project-activity-summary&decorator=none&contentOnly=true&_={timestamp_int()}', catch_response=True)

    # 535 /rest/api/2/user/properties/lastViewedVignette
    locust.client.put(f'/rest/api/2/user/properties/lastViewedVignette?'
                      f'username={locust.session_data_storage["username"]}',
                      data={"id": "priority"},
                      headers=TEXT_HEADERS,
                      catch_response=True)


def edit_issue(locust):
    params = EditIssue()
    issue = random.choice(jira_dataset['issues'])
    issue_id = issue[1]
    issue_key = issue[0]
    project_key = issue[2]

    @jira_measure('locust_edit_issue:open_editor')
    def edit_issue_open_editor():
        raise_if_login_failed(locust)

        # 700 /secure/EditIssue!default.jspa
        r = locust.get(f'/secure/EditIssue!default.jspa?id={issue_id}', catch_response=True)

        content = r.content.decode('utf-8')
        issue_type = fetch_by_re(params.issue_type_pattern, content)
        atl_token = fetch_by_re(params.atl_token_pattern, content)
        priority = fetch_by_re(params.issue_priority_pattern, content, group_no=2)
        assignee = fetch_by_re(params.issue_assigneee_reporter_pattern, content, group_no=2)
        reporter = fetch_by_re(params.issue_reporter_pattern, content)

        if not (f' Edit Issue:  [{issue_key}]' in content):
            logger.error(f'{params.err_message_issue_not_found} - {issue_id}, {issue_key}: {content}')
        assert f' Edit Issue:  [{issue_key}]' in content, \
            params.err_message_issue_not_found
        logger.locust_info(f"{params.action_name}: Editing issue {issue_key}")

        # 705 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("705"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 710 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("710"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 715 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("715"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 720 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("720"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 725 /rest/internal/2/user/mention/search
        locust.get(f'/rest/internal/2/user/mention/search?issueKey={issue_key}'
                   f'&projectKey={project_key}&maxResults=10&_={timestamp_int()}', catch_response=True)

        edit_body = f'id={issue_id}&summary={generate_random_string(15)}&issueType={issue_type}&priority={priority}' \
                    f'&dueDate=""&assignee={assignee}&reporter={reporter}&environment=""' \
                    f'&description={generate_random_string(500)}&timetracking_originalestimate=""' \
                    f'&timetracking_remainingestimate=""&isCreateIssue=""&hasWorkStarted=""&dnd-dropzone=""' \
                    f'&comment=""&commentLevel=""&atl_token={atl_token}&Update=Update'
        locust.session_data_storage['edit_issue_body'] = edit_body
        locust.session_data_storage['atl_token'] = atl_token

    edit_issue_open_editor()

    @jira_measure('locust_edit_issue:save_edit')
    def edit_issue_save_edit():
        raise_if_login_failed(locust)

        # 730 /secure/EditIssue.jspa
        r = locust.post(f'/secure/EditIssue.jspa?atl_token={locust.session_data_storage["atl_token"]}',
                        params=locust.session_data_storage['edit_issue_body'],
                        headers=TEXT_HEADERS,
                        catch_response=True)

        content = r.content.decode('utf-8')
        if not (f'[{issue_key}]' in content):
            logger.error(f'Could not save edited page: {content}')
        assert f'[{issue_key}]' in content, 'Could not save edited page'

        # 735 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("735"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 740 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("740"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 745 /rest/bamboo/latest/deploy
        locust.get(f'/rest/bamboo/latest/deploy/{project_key}/{issue_key}?_{timestamp_int()}', catch_response=True)

        # 750 /secure/AjaxIssueEditAction!default.jspa
        locust.get(f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId='
                   f'{issue_id}&_={timestamp_int()}', catch_response=True)

        # 755 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("755"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 760 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("760"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 765 /rest/projects/1.0/project/${issue_project_key}/lastVisited
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          params.last_visited_body,
                          catch_response=True)

        # 770 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("770"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

    edit_issue_save_edit()


@jira_measure('locust_view_dashboard')
def view_dashboard(locust):
    raise_if_login_failed(locust)
    params = ViewDashboard()

    # 600 /secure/Dashboard.jspa
    r = locust.get('/secure/Dashboard.jspa', catch_response=True)

    content = r.content.decode('utf-8')
    if not (f'title="loggedInUser" value="{locust.session_data_storage["username"]}">' in content):
        logger.error(f'User {locust.session_data_storage["username"]} authentication failed: {content}')
    assert f'title="loggedInUser" value="{locust.session_data_storage["username"]}">' in content, \
        'User authentication failed'

    # 605 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("605"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 610 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("610"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 615 /rest/gadget/1.0/issueTable/jql
    locust.get('/rest/gadget/1.0/issueTable/jql?num=10&tableContext=jira.table.cols.dashboard&addDefault=true'
               '&enableSorting=true&paging=true&showActions=true'
               '&jql=assignee+%3D+currentUser()+AND+resolution+%3D+unresolved+ORDER+BY+priority+'
               'DESC%2C+created+ASC&sortBy=&startIndex=0&_=1588507042019',
               catch_response=True)

    # 620 /plugins/servlet/gadgets/dashboard-diagnostics
    r = locust.post('/plugins/servlet/gadgets/dashboard-diagnostics',
                    params={'uri': f'{JIRA_SETTINGS.server_url.lower()}//secure/Dashboard.jspa'},
                    headers=TEXT_HEADERS,
                    catch_response=True)

    content = r.content.decode('utf-8')
    if not ('Dashboard Diagnostics: OK' in content):
        logger.error(f'view_dashboard dashboard-diagnostics failed: {content}')
    assert 'Dashboard Diagnostics: OK' in content, 'view_dashboard dashboard-diagnostics failed'

    # 625 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("625"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 630 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("630"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 635 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("635"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


def add_comment(locust):
    params = AddComment()
    issue = random.choice(jira_dataset['issues'])
    issue_id = issue[1]
    issue_key = issue[0]
    project_key = issue[2]

    @jira_measure('locust_add_comment:open_comment')
    def add_comment_open_comment():
        raise_if_login_failed(locust)

        # 800 /secure/AddComment!default.jspa
        r = locust.get(f'/secure/AddComment!default.jspa?id={issue_id}', catch_response=True)

        content = r.content.decode('utf-8')
        token = fetch_by_re(params.atl_token_pattern, content)
        form_token = fetch_by_re(params.form_token_pattern, content)
        if not (f'Add Comment: {issue_key}' in content):
            logger.error(f'Could not open comment in the {issue_key} issue: {content}')
        assert f'Add Comment: {issue_key}' in content, 'Could not open comment in the issue'

        # 805 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("805"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 810 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("810"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 815 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("815"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 820 /rest/internal/2/user/mention/search
        locust.get(f'/rest/internal/2/user/mention/search?issueKey={issue_key}&projectKey={project_key}'
                   f'&maxResults=10&_={timestamp_int()}', catch_response=True)
        locust.session_data_storage['token'] = token
        locust.session_data_storage['form_token'] = form_token

        # 825 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("825"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

    add_comment_open_comment()

    @jira_measure('locust_add_comment:save_comment')
    def add_comment_save_comment():
        raise_if_login_failed(locust)

        # 845 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("845"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 850 /secure/AddComment.jspa
        r = locust.post(f'/secure/AddComment.jspa?atl_token={locust.session_data_storage["token"]}',
                        params={"id": {issue_id}, "formToken": locust.session_data_storage["form_token"],
                                "dnd-dropzone": None, "comment": generate_random_string(20),
                                "commentLevel": None, "atl_token": locust.session_data_storage["token"],
                                "Add": "Add"},
                        headers=TEXT_HEADERS,
                        catch_response=True)

        content = r.content.decode('utf-8')
        if not (f'<meta name="ajs-issue-key" content="{issue_key}">' in content):
            logger.error(f'Could not save comment: {content}')
        assert f'<meta name="ajs-issue-key" content="{issue_key}">' in content, 'Could not save comment'

        # 860 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("860"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 865 /rest/bamboo/latest/deploy/${issue_project_key}/{issue_key}
        locust.get(f'/rest/bamboo/latest/deploy/{project_key}/{issue_key}?_={timestamp_int()}', catch_response=True)

        # 870 /secure/AjaxIssueEditAction!default.jspa
        locust.get(f'/secure/AjaxIssueEditAction!default.jspa?'
                   f'decorator=none'
                   f'&issueId={issue_id}'
                   f'&_={timestamp_int()}', catch_response=True)

        # 875 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("875"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 880 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("880"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 885 /rest/projects/1.0/project
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          params.browse_project_payload,
                          catch_response=True)

    add_comment_save_comment()


@jira_measure('locust_browse_projects')
def browse_projects(locust):
    raise_if_login_failed(locust)
    params = BrowseProjects()

    page = random.randint(1, jira_dataset['pages'])

    # 900 /secure/BrowseProjects.jspa
    r = locust.get(f'/secure/BrowseProjects.jspa?selectedCategory=all&selectedProjectType=all&page={page}',
                   catch_response=True)

    content = r.content.decode('utf-8')
    if not ('WRM._unparsedData["com.atlassian.jira.project.browse:projects"]="' in content):
        logger.error(f'Could not browse projects: {content}')
    assert 'WRM._unparsedData["com.atlassian.jira.project.browse:projects"]="' in content, 'Could not browse projects'

    # 905 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("905"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 910 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("910"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 915 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("915"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


@jira_measure('locust_view_kanban_board')
def view_kanban_board(locust):
    raise_if_login_failed(locust)
    kanban_board_id = random.choice(jira_dataset["kanban_boards"])[0]
    kanban_board(locust, kanban_board_id)


@jira_measure('locust_view_scrum_board')
def view_scrum_board(locust):
    raise_if_login_failed(locust)
    scrum_board_id = random.choice(jira_dataset["scrum_boards"])[0]
    scrum_board(locust, scrum_board_id)


@jira_measure('locust_view_backlog')
def view_backlog(locust):
    raise_if_login_failed(locust)
    scrum_board_id = random.choice(jira_dataset["scrum_boards"])[0]
    backlog_board(locust, scrum_board_id)


@jira_measure('locust_browse_boards')
def browse_boards(locust):
    raise_if_login_failed(locust)
    params = BrowseBoards()

    # 1300 /secure/ManageRapidViews.jspa
    locust.get('/secure/ManageRapidViews.jspa', catch_response=True)

    # 1305 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1305"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1310 /rest/greenhopper/1.0/rapidviews/viewsData
    locust.get(f'/rest/greenhopper/1.0/rapidviews/viewsData?_{timestamp_int()}', catch_response=True)

    # 1315 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1315"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1320 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("1320"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


def kanban_board(locust, board_id):
    params = ViewBoard(action_name='view_kanban_board')
    url = f'/secure/RapidBoard.jspa?rapidView={board_id}'

    # 1000 /secure/RapidBoard.jspa
    r = locust.get(url, catch_response=True)

    content = r.content.decode('utf-8')
    project_key = fetch_by_re(params.project_key_pattern, content)
    project_id = fetch_by_re(params.project_id_pattern, content)
    project_plan = fetch_by_re(params.project_plan_pattern, content, group_no=2)
    if project_plan:
        project_plan = project_plan.replace('\\', '')
    logger.locust_info(f"{params.action_name}: key = {project_key}, id = {project_id}, plan = {project_plan}")
    assert f'currentViewConfig\"{{\"id\":{board_id}', 'Could not open board'

    # 1005 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1005"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1010 /rest/greenhopper/1.0/xboard/config.json
    locust.get(f'/rest/greenhopper/1.0/xboard/config.json?'
               f'returnDefaultBoard=true'
               f'&_={timestamp_int()}', catch_response=True)

    # 1015 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1015"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1025 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("1025"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    if project_key:
        # 1030 /rest/api/2/project/${x_project_key}
        locust.get(f'/rest/api/2/project/{project_key}?_={timestamp_int()}', catch_response=True)

        # 1035 /rest/projects/1.0/project/{project_key}/lastVisited
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          {"id": f"com.pyxis.greenhopper.jira:project-sidebar-work-{project_plan}"},
                          catch_response=True)

        # 1040 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1040"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)
    else:
        # 1045 /rest/greenhopper/1.0/xboard/toolSections
        locust.get(f'/rest/greenhopper/1.0/xboard/toolSections?mode=work&rapidViewId={board_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1050 /rest/greenhopper/1.0/xboard/work/allData.json
        locust.get(f'/rest/greenhopper/1.0/xboard/work/allData.json?rapidViewId={board_id}', catch_response=True)

        if project_id:
            # 1055 /rest/greenhopper/1.0/xboard/work/transitions.json
            locust.get(f'/rest/greenhopper/1.0/xboard/work/transitions.json?'
                       f'projectId={project_id}'
                       f'&_={timestamp_int()}')

        # 1060 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1060"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

    if project_key:
        # 1065 /rest/projects/1.0/project/{project_key}/lastVisited
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          {"id": f"com.pyxis.greenhopper.jira:project-sidebar-work-{project_plan}"},
                          catch_response=True)


def scrum_board(locust, board_id):
    params = ViewBoard(action_name='view_scrum_board')

    # 1100 /secure/RapidBoard.jspa
    r = locust.get(f'/secure/RapidBoard.jspa?rapidView={board_id}', catch_response=True)

    content = r.content.decode('utf-8')
    project_key = fetch_by_re(params.project_key_pattern, content)
    project_id = fetch_by_re(params.project_id_pattern, content)
    project_plan = fetch_by_re(params.project_plan_pattern, content, group_no=2)
    if project_plan:
        project_plan = project_plan.replace('\\', '')
    logger.locust_info(f"{params.action_name}: key = {project_key}, id = {project_id}, plan = {project_plan}")
    assert f'currentViewConfig\"{{\"id\":{board_id}', 'Could not open board'

    # 1110 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1110"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1115 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1115"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    if project_key:
        # 1105 /rest/greenhopper/1.0/xboard/work/allData.json
        locust.get(f'/rest/greenhopper/1.0/xboard/work/allData.json?'
                   f'rapidViewId={board_id}'
                   f'&selectedProjectKey={project_key}',
                   catch_response=True)

        # 1120 /rest/api/2/project/{x_project_key}
        locust.get(f'/rest/api/2/project/{project_key}?'
                   f'_={timestamp_int()}',
                   catch_response=True)

        # 1125 /rest/greenhopper/1.0/xboard/toolSections
        locust.get(f'/rest/greenhopper/1.0/xboard/toolSections?'
                   f'mode=work'
                   f'&rapidViewId={board_id}'
                   f'&selectedProjectKey={project_key}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1130 /rest/greenhopper/1.0/xboard/work/allData.json
        locust.get(f'/rest/greenhopper/1.0/xboard/work/allData.json?'
                   f'rapidViewId={board_id}'
                   f'&selectedProjectKey={project_key}',
                   catch_response=True)

        # 1060 /rest/projects/1.0/project/{project_key}/lastVisited
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          {"id": f"com.pyxis.greenhopper.jira:project-sidebar-work-{project_plan}"},
                          catch_response=True)

    if not project_key:
        # 1140 /rest/greenhopper/1.0/xboard/toolSections
        locust.get(f'/rest/greenhopper/1.0/xboard/toolSections?'
                   f'mode=work'
                   f'&rapidViewId={board_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1145 /rest/greenhopper/1.0/xboard/work/allData.json
        locust.get(f'/rest/greenhopper/1.0/xboard/work/allData.json?'
                   f'rapidViewId={board_id}',
                   catch_response=True)

    # 1150 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1150"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1155 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1155"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1165 /rest/analytics/1.0/publish/bulk
    locust.post('/rest/analytics/1.0/publish/bulk',
                json=params.resources_body.get("1165"),
                headers=RESOURCE_HEADERS,
                catch_response=True)


def backlog_board(locust, board_id):
    params = ViewBoard(action_name='view_backlog')

    # 1200 /secure/RapidBoard.jspa
    r = locust.get(f'/secure/RapidBoard.jspa?'
                   f'rapidView={board_id}'
                   f'&view=planning',
                   catch_response=True)

    content = r.content.decode('utf-8')
    project_key = fetch_by_re(params.project_key_pattern, content)
    project_id = fetch_by_re(params.project_id_pattern, content)
    project_plan = fetch_by_re(params.project_plan_pattern, content, group_no=2)
    if project_plan:
        project_plan = project_plan.replace('\\', '')
    logger.locust_info(f"{params.action_name}: key = {project_key}, id = {project_id}, plan = {project_plan}")
    assert f'currentViewConfig\"{{\"id\":{board_id}', 'Could not open board'

    # 1210 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1210"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    # 1215 /rest/webResources/1.0/resources
    locust.post('/rest/webResources/1.0/resources',
                json=params.resources_body.get("1215"),
                headers=RESOURCE_HEADERS,
                catch_response=True)

    if project_key:
        # 1205 /rest/greenhopper/1.0/xboard/plan/backlog/data.json
        locust.get(f'/rest/greenhopper/1.0/xboard/plan/backlog/data.json?'
                   f'rapidViewId={board_id}'
                   f'&selectedProjectKey={project_key}',
                   catch_response=True)

        # 1235 /rest/api/2/project/{project_key}
        locust.get(f'/rest/api/2/project/{project_key}?_={timestamp_int()}', catch_response=True)

        # 1240 /rest/greenhopper/1.0/xboard/toolSections
        locust.get(f'/rest/greenhopper/1.0/xboard/toolSections?'
                   f'mode=plan'
                   f'&rapidViewId={board_id}'
                   f'&selectedProjectKey={project_key}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1245 /rest/greenhopper/1.0/xboard/plan/backlog/data.json
        locust.get(f'/rest/greenhopper/1.0/xboard/plan/backlog/data.json?'
                   f'&rapidViewId={board_id}'
                   f'&selectedProjectKey={project_key}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1250 /rest/inline-create/1.0/context/bootstrap
        locust.get(f'/rest/inline-create/1.0/context/bootstrap?'
                   f'&query=project = {project_key} ORDER BY Rank ASC'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1255 /rest/webResources/1.0/resources
        locust.post('/rest/webResources/1.0/resources',
                    json=params.resources_body.get("1255"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1260 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1260"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1265 /rest/analytics/1.0/publish/bulk
        locust.post('/rest/analytics/1.0/publish/bulk',
                    json=params.resources_body.get("1265"),
                    headers=RESOURCE_HEADERS,
                    catch_response=True)

        # 1285 /rest/projects/1.0/project/{project_key}/lastVisited
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          {"id": f"com.pyxis.greenhopper.jira:project-sidebar-work-{project_plan}"},
                          catch_response=True)

    if not project_key:
        # 1270 /rest/greenhopper/1.0/xboard/toolSections
        locust.get(f'/rest/greenhopper/1.0/xboard/toolSections?'
                   f'mode=plan'
                   f'&rapidViewId={board_id}'
                   f'&_={timestamp_int()}',
                   catch_response=True)

        # 1275 /rest/greenhopper/1.0/xboard/plan/backlog/data.json
        locust.get(f'/rest/greenhopper/1.0/xboard/plan/backlog/data.json?'
                   f'rapidViewId={board_id}',
                   catch_response=True)

    # 1280 /rest/greenhopper/1.0/rapidviewconfig/editmodel.json
    locust.get(f'/rest/greenhopper/1.0/rapidviewconfig/editmodel.json?'
               f'rapidViewId={board_id}'
               f'&_={timestamp_int()}',
               catch_response=True)
