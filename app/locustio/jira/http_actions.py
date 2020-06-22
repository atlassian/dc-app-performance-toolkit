import random
import re
from locust.exception import ResponseError
from locustio.jira.requests_params import Login, BrowseIssue, CreateIssue, SearchJql, ViewBoard, BrowseBoards, \
    BrowseProjects, AddComment, ViewDashboard, EditIssue, ViewProjectSummary, jira_datasets
from locustio.common_utils import jira_measure, fetch_by_re, timestamp_int, generate_random_string, TEXT_HEADERS, \
    ADMIN_HEADERS, NO_TOKEN_HEADERS, init_logger

from util.conf import JIRA_SETTINGS

logger = init_logger(app_type='jira')
jira_dataset = jira_datasets()


@jira_measure
def login_and_view_dashboard(locust):
    params = Login()

    user = random.choice(jira_dataset["users"])
    body = params.login_body
    body['os_username'] = user[0]
    body['os_password'] = user[1]

    locust.client.post('/login.jsp', body, TEXT_HEADERS, catch_response=True)
    r = locust.client.get('/', catch_response=True)
    if not r.content:
        raise Exception('Please check server hostname in jira.yml file')
    content = r.content.decode('utf-8')
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("110"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post("/plugins/servlet/gadgets/dashboard-diagnostics",
                       {"uri": f"{locust.client.base_url.lower()}/secure/Dashboard.jspa"},
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("120"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("125"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("130"),
                       TEXT_HEADERS, catch_response=True)

    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.get(f'/rest/gadget/1.0/issueTable/jql?num=10&tableContext=jira.table.cols.dashboard'
                      f'&addDefault=true&enableSorting=true&paging=true&showActions=true'
                      f'&jql=assignee+%3D+currentUser()+AND'
                      f'+resolution+%3D+unresolved+ORDER+BY+priority+DESC%2C+created+ASC'
                      f'&sortBy=&startIndex=0&_={timestamp_int()}', catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=5&relativeLinks=true&_={timestamp_int()}',
                      catch_response=True)
    # Assertions
    token = fetch_by_re(params.atl_token_pattern, content)
    if not (f'title="loggedInUser" value="{user[0]}">' in content):
        logger.error(f'User {user[0]} authentication failed: {content}')
    assert f'title="loggedInUser" value="{user[0]}">' in content, 'User authentication failed'
    locust.user = user[0]
    locust.atl_token = token
    locust.storage = dict()  # Define locust storage dict for getting cross-functional variables access
    logger.locust_info(f"{params.action_name}: User {user[0]} logged in with atl_token: {token}")


@jira_measure
def view_issue(locust):
    params = BrowseIssue()
    issue_key = random.choice(jira_dataset['issues'])[0]
    project_key = random.choice(jira_dataset['issues'])[2]

    r = locust.client.get(f'/browse/{issue_key}', catch_response=True)
    content = r.content.decode('utf-8')
    issue_id = fetch_by_re(params.issue_id_pattern, content)
    project_avatar_id = fetch_by_re(params.project_avatar_id_pattern, content)
    edit_allowed = fetch_by_re(params.edit_allow_pattern, content, group_no=0)
    locust.client.get(f'/secure/projectavatar?avatarId={project_avatar_id}', catch_response=True)
    # Assertions
    if not(f'<meta name="ajs-issue-key" content="{issue_key}">' in content):
        logger.error(f'Issue {issue_key} not found: {content}')
    assert f'<meta name="ajs-issue-key" content="{issue_key}">' in content, 'Issue not found'
    logger.locust_info(f"{params.action_name}: Issue {issue_key} is opened successfully")

    logger.locust_info(f'{params.action_name}: Issue key - {issue_key}, issue_id - {issue_id}')
    if edit_allowed:
        url = f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId={issue_id}&_={timestamp_int()}'
        locust.client.get(url, catch_response=True)
    locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited', params.browse_project_payload,
                      catch_response=True)


def create_issue(locust):
    params = CreateIssue()
    project = random.choice(jira_dataset['projects'])
    project_id = project[1]

    @jira_measure
    def create_issue_open_quick_create():
        r = locust.client.post('/secure/QuickCreateIssue!default.jspa?decorator=none',
                               ADMIN_HEADERS, catch_response=True)
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
        locust.client.post('/rest/quickedit/1.0/userpreferences/create', params.user_preferences_payload,
                           ADMIN_HEADERS, catch_response=True)
        locust.storage['issue_body_params_dict'] = issue_body_params_dict
    create_issue_open_quick_create()

    @jira_measure
    def create_issue_submit_form():
        issue_body = params.prepare_issue_body(locust.storage['issue_body_params_dict'], user=locust.user)
        r = locust.client.post('/secure/QuickCreateIssue.jspa?decorator=none', params=issue_body,
                               headers=ADMIN_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if not ('"id":"project","label":"Project"') in content:
            logger.error(f'{params.err_message_create_issue}: {content}')
        assert '"id":"project","label":"Project"' in content, params.err_message_create_issue
        issue_key = fetch_by_re(params.create_issue_key_pattern, content)
        logger.locust_info(f"{params.action_name}: Issue {issue_key} was successfully created")
    create_issue_submit_form()
    locust.storage.clear()


@jira_measure
def search_jql(locust):
    params = SearchJql()
    jql = random.choice(jira_dataset['jqls'])[0]

    r = locust.client.get(f'/issues/?jql={jql}', catch_response=True)
    content = r.content.decode('utf-8')
    if not (locust.atl_token in content):
        logger.error(f'Can not search by {jql}: {content}')
    assert locust.atl_token in content, 'Can not search by jql'

    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("305"),
                       TEXT_HEADERS, catch_response=True)

    locust.client.get(f'/rest/api/2/filter/favourite?expand=subscriptions[-5:]&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/issueNav/latest/preferredSearchLayout', params={'layoutKey': 'split-view'},
                       headers=NO_TOKEN_HEADERS, catch_response=True)

    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("320"),
                       TEXT_HEADERS, catch_response=True)
    r = locust.client.post('/rest/issueNav/1/issueTable', data=params.issue_table_payload,
                           headers=NO_TOKEN_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')
    issue_ids = re.findall(params.ids_pattern, content)

    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("330"),
                       TEXT_HEADERS, catch_response=True)
    if issue_ids:
        body = params.prepare_jql_body(issue_ids)
        r = locust.client.post('/rest/issueNav/1/issueTable/stable', data=body,
                               headers=NO_TOKEN_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        issue_key = fetch_by_re(params.issue_key_pattern, content)
        issue_id = fetch_by_re(params.issue_id_pattern, content)
    locust.client.post('/secure/QueryComponent!Jql.jspa', params={'jql': 'order by created DESC',
                                                                  'decorator': None}, headers=TEXT_HEADERS,
                       catch_response=True)
    locust.client.post('/rest/orderbycomponent/latest/orderByOptions/primary',
                       data={"jql": "order by created DESC"}, headers=TEXT_HEADERS, catch_response=True)
    if issue_ids:
        r = locust.client.post('/secure/AjaxIssueAction!default.jspa', params={"decorator": None,
                                                                               "issueKey": issue_key,
                                                                               "prefetch": False,
                                                                               "shouldUpdateCurrentProject": False,
                                                                               "loadFields": False,
                                                                               "_": timestamp_int()},
                               headers=TEXT_HEADERS, catch_response=True)
        if params.edit_allow_string in r.content.decode('utf-8'):
            locust.client.get(f'/secure/AjaxIssueEditAction!default.jspa?'
                              f'decorator=none&issueId={issue_id}&_={timestamp_int()}', catch_response=True)


@jira_measure
def view_project_summary(locust):
    params = ViewProjectSummary()
    project = random.choice(jira_dataset['projects'])
    project_key = project[0]

    r = locust.client.get(f'/projects/{project_key}/summary', catch_response=True)
    content = r.content.decode('utf-8')
    logger.locust_info(f"{params.action_name}. View project {project_key}: {content}")

    assert_string = f'["project-key"]="\\"{project_key}\\"'
    if not (assert_string in content):
        logger.error(f'{params.err_message} {project_key}')
    assert assert_string in content, f'{params.err_message}'

    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("505"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("510"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("520"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=10&relativeLinks=true&streams=key+IS+{project_key}'
                      f'&providers=thirdparty+dvcs-streams-provider+issues&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("530"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/projects/{project_key}?selectedItem=com.atlassian.jira.jira-projects-plugin:'
                      f'project-activity-summary&decorator=none&contentOnly=true&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("545"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.put(f'/rest/api/2/user/properties/lastViewedVignette?username={locust.user}', data={"id": "priority"},
                      headers=TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("555"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=10&relativeLinks=true&streams=key+IS+{project_key}'
                      f'&providers=thirdparty+dvcs-streams-provider+issues&_={timestamp_int()}',
                      catch_response=True)


def edit_issue(locust):
    params = EditIssue()
    issue = random.choice(jira_dataset['issues'])
    issue_id = issue[1]
    issue_key = issue[0]
    project_key = issue[2]

    @jira_measure
    def edit_issue_open_editor():
        r = locust.client.get(f'/secure/EditIssue!default.jspa?id={issue_id}', catch_response=True)
        content = r.content.decode('utf-8')

        issue_type = fetch_by_re(params.issue_type_pattern, content)
        atl_token = fetch_by_re(params.atl_token_pattern, content)
        priority = fetch_by_re(params.issue_priority_pattern, content, group_no=2)
        assignee = fetch_by_re(params.issue_assigneee_reporter_pattern, content, group_no=2)
        reporter = fetch_by_re(params.issue_reporter_pattern, content)

        if not (f' Edit Issue:  [{issue_key}]' in content):
            logger.error(f'{params.err_message_issue_not_found} - {issue_id}, {issue_key}: {content}')
        assert f' Edit Issue:  [{issue_key}]' in content, \
            f'{params.err_message_issue_not_found}.'
        logger.locust_info(f"{params.action_name}: Editing issue {issue_key}")

        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("705"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("710"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("720"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/rest/internal/2/user/mention/search?issueKey={issue_key}'
                          f'&projectKey={project_key}&maxResults=10&_={timestamp_int()}', catch_response=True)

        edit_body = f'id={issue_id}&summary={generate_random_string(15)}&issueType={issue_type}&priority={priority}' \
                    f'&dueDate=""&assignee={assignee}&reporter={reporter}&environment=""' \
                    f'&description={generate_random_string(500)}&timetracking_originalestimate=""' \
                    f'&timetracking_remainingestimate=""&isCreateIssue=""&hasWorkStarted=""&dnd-dropzone=""' \
                    f'&comment=""&commentLevel=""&atl_token={atl_token}&Update=Update'
        locust.storage['edit_issue_body'] = edit_body
        locust.storage['atl_token'] = atl_token
    edit_issue_open_editor()

    @jira_measure
    def edit_issue_save_edit():
        r = locust.client.post(f'/secure/EditIssue.jspa?atl_token={locust.storage["atl_token"]}',
                               params=locust.storage['edit_issue_body'],
                               headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if not (f'[{issue_key}]' in content):
            logger.error(f'Could not save edited page: {content}')
        assert f'[{issue_key}]' in content, 'Could not save edited page'

        locust.client.get(f'/browse/{issue_key}', catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("740"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("745"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("765"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId='
                          f'{issue_id}&_={timestamp_int()}', catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("775"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited', params.last_visited_body,
                          catch_response=True)
    edit_issue_save_edit()
    locust.storage.clear()


@jira_measure
def view_dashboard(locust):
    params = ViewDashboard()

    r = locust.client.get('/secure/Dashboard.jspa', catch_response=True)
    content = r.content.decode('utf-8')
    if not (f'title="loggedInUser" value="{locust.user}">' in content):
        logger.error(f'User {locust.user} authentication failed: {content}')
    assert f'title="loggedInUser" value="{locust.user}">' in content, 'User authentication failed'
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("605"),
                       TEXT_HEADERS, catch_response=True)
    r = locust.client.post('/plugins/servlet/gadgets/dashboard-diagnostics',
                           params={'uri': f'{JIRA_SETTINGS.server_url.lower()}//secure/Dashboard.jspa'},
                           headers=TEXT_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')
    if not ('Dashboard Diagnostics: OK' in content):
        logger.error(f'view_dashboard dashboard-diagnostics failed: {content}')
    assert 'Dashboard Diagnostics: OK' in content, 'view_dashboard dashboard-diagnostics failed'
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("620"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.get(f'/rest/gadget/1.0/issueTable/jql?num=10&tableContext=jira.table.cols.dashboard&addDefault=true'
                      f'&enableSorting=true&paging=true&showActions=true'
                      f'&jql=assignee+%3D+currentUser()+AND+resolution+%3D+unresolved+ORDER+BY+priority+'
                      f'DESC%2C+created+ASC&sortBy=&startIndex=0&_=1588507042019', catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=5&relativeLinks=true&_={timestamp_int()}',
                      catch_response=True)


def add_comment(locust):
    params = AddComment()
    issue = random.choice(jira_dataset['issues'])
    issue_id = issue[1]
    issue_key = issue[0]
    project_key = issue[2]

    @jira_measure
    def add_comment_open_comment():
        r = locust.client.get(f'/secure/AddComment!default.jspa?id={issue_id}', catch_response=True)
        content = r.content.decode('utf-8')
        token = fetch_by_re(params.atl_token_pattern, content)
        form_token = fetch_by_re(params.form_token_pattern, content)
        if not (f'Add Comment: {issue_key}' in content):
            logger.error(f'Could not open comment in the {issue_key} issue: {content}')
        assert f'Add Comment: {issue_key}' in content, 'Could not open comment in the issue'

        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("805"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("810"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("820"),
                           TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/rest/internal/2/user/mention/search?issueKey={issue_key}&projectKey={project_key}'
                          f'&maxResults=10&_={timestamp_int()}', catch_response=True)
        locust.storage['token'] = token
        locust.storage['form_token'] = form_token
    add_comment_open_comment()

    @jira_measure
    def add_comment_save_comment():
        r = locust.client.post(f'/secure/AddComment.jspa?atl_token={locust.storage["token"]}',
                               params={"id": {issue_id}, "formToken": locust.storage["form_token"],
                                       "dnd-dropzone": None, "comment": generate_random_string(20),
                                       "commentLevel": None, "atl_token": locust.storage["token"],
                                       "Add": "Add"}, headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        if not (f'<meta name="ajs-issue-key" content="{issue_key}">' in content):
            logger.error(f'Could not save comment: {content}')
        assert f'<meta name="ajs-issue-key" content="{issue_key}">' in content, 'Could not save comment'
    add_comment_save_comment()
    locust.storage.clear()


@jira_measure
def browse_projects(locust):
    params = BrowseProjects()

    page = random.randint(1, jira_dataset['pages'])
    r = locust.client.get(f'/secure/BrowseProjects.jspa?selectedCategory=all&selectedProjectType=all&page={page}',
                          catch_response=True)
    content = r.content.decode('utf-8')
    if not ('WRM._unparsedData["com.atlassian.jira.project.browse:projects"]="' in content):
        logger.error(f'Could not browse projects: {content}')
    assert 'WRM._unparsedData["com.atlassian.jira.project.browse:projects"]="' in content, 'Could not browse projects'
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("905"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("910"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("920"),
                       TEXT_HEADERS, catch_response=True)


@jira_measure
def view_kanban_board(locust):
    kanban_board_id = random.choice(jira_dataset["kanban_boards"])[0]
    view_board(locust, kanban_board_id)


@jira_measure
def view_scrum_board(locust):
    scrum_board_id = random.choice(jira_dataset["scrum_boards"])[0]
    view_board(locust, scrum_board_id)


@jira_measure
def view_backlog(locust):
    scrum_board_id = random.choice(jira_dataset["scrum_boards"])[0]
    view_board(locust, scrum_board_id, view_backlog=True)


@jira_measure
def browse_boards(locust):
    params = BrowseBoards()
    locust.client.get('/secure/ManageRapidViews.jspa', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1205"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1210"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1215"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1225"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/greenhopper/1.0/rapidviews/viewsData?_{timestamp_int()}', catch_response=True)


def view_board(locust, board_id, view_backlog=False):
    params = ViewBoard()
    if view_backlog:
        url = f'/secure/RapidBoard.jspa?rapidView={board_id}&view=planning'
    else:
        url = f'/secure/RapidBoard.jspa?rapidView={board_id}'

    r = locust.client.get(url, catch_response=True)
    content = r.content.decode('utf-8')
    project_key = fetch_by_re(params.project_key_pattern, content)
    project_id = fetch_by_re(params.project_id_pattern, content)
    project_plan = fetch_by_re(params.project_plan_pattern, content, group_no=2)
    if project_plan:
        project_plan = project_plan.replace('\\', '')
    logger.locust_info(f"{params.action_name}: key = {project_key}, id = {project_id}, plan = {project_plan}")
    assert f'currentViewConfig\"{{\"id\":{board_id}', 'Could not open board'

    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1000"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1005"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1010"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1015"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1020"),
                       TEXT_HEADERS, catch_response=True)

    if project_key:
        locust.client.get(f'/rest/api/2/project/{project_key}?_={timestamp_int()}', catch_response=True)
        locust.client.get(f'/rest/greenhopper/1.0/xboard/toolSections?mode=work&rapidViewId={board_id}'
                          f'&selectedProjectKey={project_key}&_={timestamp_int()}', catch_response=True)
        locust.client.get(f'/rest/greenhopper/1.0/xboard/work/allData.json?rapidViewId={board_id}'
                          f'&selectedProjectKey={project_key}&_={timestamp_int()}', catch_response=True)
        if view_backlog:
            locust.client.get(f'/rest/inline-create/1.0/context/bootstrap?query='
                              f'project%20%3D%20{project_key}%20ORDER%20BY%20Rank%20ASC&&_={timestamp_int()}',
                              catch_response=True)
    else:
        locust.client.get(f'/rest/greenhopper/1.0/xboard/toolSections?mode=work&rapidViewId={board_id}'
                          f'&_={timestamp_int()}', catch_response=True)
        locust.client.get(f'/rest/greenhopper/1.0/xboard/work/allData.json?rapidViewId={board_id}'
                          f'&selectedProjectKey={project_key}', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1025"),
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.resources_body.get("1030"),
                       TEXT_HEADERS, catch_response=True)
    if view_backlog:
        locust.client.get(f'/rest/greenhopper/1.0/rapidviewconfig/editmodel.json?rapidViewId={board_id}'
                          f'&_={timestamp_int()}', catch_response=True)
    if project_key:
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          {"id": f"com.pyxis.greenhopper.jira:project-sidebar-work-{project_plan}"},
                          catch_response=True)
