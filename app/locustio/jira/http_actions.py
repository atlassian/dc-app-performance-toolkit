import itertools
import inspect
from locust.exception import ResponseError
from locustio.jira.requests_params import *

from util.conf import JIRA_SETTINGS

counter = itertools.count()


@measure
def login_and_view_dashboard(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    params = Login()

    user = random.choice(jira_dataset["users"])
    body = params.login_body
    body['os_username'] = user[0]
    body['os_password'] = user[1]

    locust.client.post('/login.jsp', body, TEXT_HEADERS, catch_response=True)
    r = locust.client.get('/', catch_response=True)
    content = r.content.decode('utf-8')
    locust.client.post('/rest/webResources/1.0/resources', params.body["1"],
                       TEXT_HEADERS, catch_response=True)
    locust.client.post("/plugins/servlet/gadgets/dashboard-diagnostics",
                       {"uri": f"{locust.client.base_url.lower()}/secure/Dashboard.jspa"},
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["2"],
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["3"],
                       TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["4"],
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
    if not token:
        locust.logger.info(f'{content}')
        raise ResponseError(ERR_TOKEN_NOT_FOUND)
    assert f'title="loggedInUser" value="{user[0]}">' in content, f'User {user[0]} authentication failed'
    locust.user = user[0]
    locust.atl_token = token
    locust.storage = dict()  # Define locust storage dict for getting cross-functional variables access
    locust.logger.info(f"User {user[0]} logged in with atl_token: {token}")


@measure
def view_issue(locust):
    func_name = inspect.stack()[0][3]
    issue_key = random.choice(jira_dataset['issues'])[0]
    project_key = random.choice(jira_dataset['issues'])[2]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    params = BrowseIssue()

    r = locust.client.get(f'/browse/{issue_key}', catch_response=True)
    content = r.content.decode('utf-8')
    issue_id = fetch_by_re(params.issue_id_pattern, content)
    project_avatar_id = fetch_by_re(params.project_avatar_id_pattern, content)
    edit_allowed = fetch_by_re(params.edit_allow_pattern, content, group_no=0)
    locust.client.get(f'/secure/projectavatar?avatarId={project_avatar_id}', catch_response=True)
    # Assertions
    assert f'<meta name="ajs-issue-key" content="{issue_key}">' in content, f'Issue {issue_key} not found'
    locust.logger.info(f"Issue {issue_key} is opened successfully")

    locust.logger.info(f'Issue key: {issue_key}, issue_id {issue_id}')
    if edit_allowed:
        url = f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId={issue_id}&_={timestamp_int()}'
        locust.client.get(url, catch_response=True)
    locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited', params.browse_project_payload,
                      catch_response=True)


def create_issue(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    params = CreateIssue()

    @measure
    def create_issue_open_quick_create():
        func_name = inspect.stack()[0][3]
        locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
        r = locust.client.post('/secure/QuickCreateIssue!default.jspa?decorator=none',
                               ADMIN_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        atl_token = fetch_by_re(params.atl_token_pattern, content)
        form_token = fetch_by_re(params.form_token_pattern, content)
        issue_type = fetch_by_re(params.issue_type_pattern, content)
        project_id = fetch_by_re(params.project_id_pattern, content)
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
        assert params.create_issue_assertion in content, ERR_CREATE_ISSUE
        locust.client.post('/rest/quickedit/1.0/userpreferences/create', params.user_preferences_payload,
                           ADMIN_HEADERS, catch_response=True)
        locust.storage['issue_body_params_dict'] = issue_body_params_dict
    create_issue_open_quick_create()

    @measure
    def create_issue_submit_form():
        issue_body = params.prepare_issue_body(locust.storage['issue_body_params_dict'], user=locust.user)
        r = locust.client.post('/secure/QuickCreateIssue.jspa?decorator=none', params=issue_body,
                               headers=ADMIN_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')

        assert params.create_issue_assertion in content, ERR_CREATE_ISSUE
        issue_key = fetch_by_re(params.create_issue_key_pattern, content)
        locust.logger.info(f"Issue {issue_key} was successfully created")
    create_issue_submit_form()
    locust.storage.clear()


@measure
def search_jql(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    jql = random.choice(jira_dataset['jqls'])[0]
    params = SearchJql()

    r = locust.client.get(f'/issues/?jql={jql}', catch_response=True)
    assert locust.atl_token in r.content.decode('utf-8'), f'Can not search by {jql}'

    locust.client.post('/rest/webResources/1.0/resources', params.body["1"],
                       TEXT_HEADERS, catch_response=True)

    locust.client.get(f'/rest/api/2/filter/favourite?expand=subscriptions[-5:]&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/issueNav/latest/preferredSearchLayout', params={'layoutKey': 'split-view'},
                       headers=NO_TOKEN_HEADERS, catch_response=True)

    locust.client.post('/rest/webResources/1.0/resources', params.body["2"],
                       TEXT_HEADERS, catch_response=True)
    r = locust.client.post('/rest/issueNav/1/issueTable', data=params.issue_table_payload,
                           headers=NO_TOKEN_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')
    issue_ids = re.findall(params.ids_pattern, content)

    locust.client.post('/rest/webResources/1.0/resources', params.body["3"],
                       TEXT_HEADERS, catch_response=True)
    if issue_ids:
        body = params.prepare_jql_body(issue_ids)
        r = locust.client.post('/rest/issueNav/1/issueTable/stable', data=body,
                               headers=NO_TOKEN_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        issue_key = fetch_by_re(params.issue_key_pattern, content)
        issue_id = fetch_by_re(params.issue_id_pattern, content)
        locust.logger.info(f"issue_key: {issue_key}, issue_id: {issue_id}")
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


@measure
def view_project_summary(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    project_key = random.choice(jira_dataset["issues"])[2]
    params = ViewProjectSummary()

    r = locust.client.get(f'/projects/{project_key}/summary', catch_response=True)
    content = r.content.decode('utf-8')
    locust.logger.info(f"View project {project_key}")

    assert_string = f'["project-key"]="\\"{project_key}\\"'
    assert assert_string in content, f'{ERR_VIEW_PROJECT_SUMMARY} {project_key}'

    locust.client.post('/rest/webResources/1.0/resources', params.body["1"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["2"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["3"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=10&relativeLinks=true&streams=key+IS+{project_key}'
                      f'&providers=thirdparty+dvcs-streams-provider+issues&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["4"], TEXT_HEADERS, catch_response=True)
    r = locust.client.get(f'/projects/{project_key}?selectedItem=com.atlassian.jira.jira-projects-plugin:'
                          f'project-activity-summary&decorator=none&contentOnly=true&_={timestamp_int()}',
                          catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["5"], TEXT_HEADERS, catch_response=True)
    locust.client.put(f'/rest/api/2/user/properties/lastViewedVignette?username={locust.user}', data={"id": "priority"},
                      headers=TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["6"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=10&relativeLinks=true&streams=key+IS+{project_key}'
                      f'&providers=thirdparty+dvcs-streams-provider+issues&_={timestamp_int()}',
                      catch_response=True)


def edit_issue(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    issue = random.choice(jira_dataset['issues'])
    issue_id = issue[1]
    issue_key = issue[0]
    project_key = issue[2]
    params = EditIssue()

    @measure
    def edit_issue_open_editor():
        r = locust.client.get(f'/secure/EditIssue!default.jspa?id={issue_id}', catch_response=True)
        content = r.content.decode('utf-8')

        issue_type = fetch_by_re(params.issue_type_pattern, content)
        atl_token = fetch_by_re(params.atl_token_pattern, content)
        priority = fetch_by_re(params.issue_priority_pattern, content, group_no=2)
        assignee = fetch_by_re(params.issue_assigneee_reporter_pattern, content, group_no=2)
        reporter = fetch_by_re(params.issue_reporter_pattern, content)

        assert f' Edit Issue:  [{issue_key}]' in content, f'{ERR_EDIT_ISSUE} - {issue_id}, {issue_key}'
        locust.logger.info(f"Editing issue {issue_key}")

        locust.client.post('/rest/webResources/1.0/resources', params.body["1"], TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["2"], TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["3"], TEXT_HEADERS, catch_response=True)
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

    @measure
    def edit_issue_save_edit():
        r = locust.client.post(f'/secure/EditIssue.jspa?atl_token={locust.storage["atl_token"]}',
                               params=locust.storage['edit_issue_body'],
                               headers=TEXT_HEADERS, catch_response=True)
        assert f'[{issue_key}]' in r.content.decode('utf-8')

        locust.client.get(f'/browse/{issue_key}', catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["4"], TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["5"], TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["6"], TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId='
                          f'{issue_id}&_={timestamp_int()}', catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["7"], TEXT_HEADERS, catch_response=True)
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited', params.last_visited_body,
                          catch_response=True)
    edit_issue_save_edit()
    locust.storage.clear()


@measure
def view_dashboard(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    params = ViewDashboard()

    r = locust.client.get('/secure/Dashboard.jspa', catch_response=True)
    content = r.content.decode('utf-8')
    assert f'title="loggedInUser" value="{locust.user}">' in content, f'User {locust.user} authentication failed'
    locust.client.post('/rest/webResources/1.0/resources', params.body["1"], TEXT_HEADERS, catch_response=True)
    r = locust.client.post('/plugins/servlet/gadgets/dashboard-diagnostics',
                           params={'uri': f'{JIRA_SETTINGS.server_url.lower()}//secure/Dashboard.jspa'},
                           headers=TEXT_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')
    assert 'Dashboard Diagnostics: OK' in content, 'view_dashboard dashboard-diagnostics failed'
    locust.client.post('/rest/webResources/1.0/resources', params.body["2"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.get(f'/rest/gadget/1.0/issueTable/jql?num=10&tableContext=jira.table.cols.dashboard&addDefault=true'
                      f'&enableSorting=true&paging=true&showActions=true'
                      f'&jql=assignee+%3D+currentUser()+AND+resolution+%3D+unresolved+ORDER+BY+priority+'
                      f'DESC%2C+created+ASC&sortBy=&startIndex=0&_=1588507042019', catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=5&relativeLinks=true&_={timestamp_int()}',
                      catch_response=True)


def add_comment(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    issue = random.choice(jira_dataset['issues'])
    issue_id = issue[1]
    issue_key = issue[0]
    project_key = issue[2]
    params = AddComment()

    @measure
    def add_comment_open_comment():
        func_name = inspect.stack()[0][3]
        locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
        r = locust.client.get(f'/secure/AddComment!default.jspa?id={issue_id}', catch_response=True)
        content = r.content.decode('utf-8')
        token = fetch_by_re(params.atl_token_pattern, content)
        form_token = fetch_by_re(params.form_token_pattern, content)
        assert f'Add Comment: {issue_key}' in content, f'Could not open comment in the {issue_key} issue'

        locust.client.post('/rest/webResources/1.0/resources', params.body["1"], TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["2"], TEXT_HEADERS, catch_response=True)
        locust.client.post('/rest/webResources/1.0/resources', params.body["3"], TEXT_HEADERS, catch_response=True)
        locust.client.get(f'/rest/internal/2/user/mention/search?issueKey={issue_key}&projectKey={project_key}'
                          f'&maxResults=10&_={timestamp_int()}', catch_response=True)
        locust.storage['token'] = token
        locust.storage['form_token'] = form_token
    add_comment_open_comment()

    @measure
    def add_comment_save_comment():
        func_name = inspect.stack()[0][3]
        locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
        r = locust.client.post(f'/secure/AddComment.jspa?atl_token={locust.storage["token"]}',
                               params={"id": {issue_id}, "formToken": locust.storage["form_token"],
                                       "dnd-dropzone": None, "comment": generate_random_string(20),
                                       "commentLevel": None, "atl_token": locust.storage["token"],
                                       "Add": "Add"}, headers=TEXT_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        assert f'<meta name="ajs-issue-key" content="{issue_key}">' in content, 'Could not save comment'
    add_comment_save_comment()
    locust.storage.clear()


@measure
def browse_projects(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    params = BrowseProjects()

    page = random.randint(1, jira_dataset['pages'])
    r = locust.client.get(f'/secure/BrowseProjects.jspa?selectedCategory=all&selectedProjectType=all&page={page}',
                          catch_response=True)
    content = r.content.decode('utf-8')
    assert params.assertion_string in content, 'Could not browse projects'
    locust.client.post('/rest/webResources/1.0/resources', params.body["1"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["2"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["3"], TEXT_HEADERS, catch_response=True)


@measure
def view_kanban_board(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    kanban_board_id = random.choice(jira_dataset["kanban_boards"])[0]
    view_board(locust, kanban_board_id)


@measure
def view_scrum_board(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    scrum_board_id = random.choice(jira_dataset["scrum_boards"])[0]
    view_board(locust, scrum_board_id)


@measure
def view_backlog(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    scrum_board_id = random.choice(jira_dataset["scrum_boards"])[0]
    view_board(locust, scrum_board_id, view_backlog=True)


@measure
def browse_boards(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    locust.client.get('/secure/ManageRapidViews.jspa', catch_response=True)
    params = BrowseBoards()
    locust.client.post('/rest/webResources/1.0/resources', params.body["1"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["2"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["3"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["4"], TEXT_HEADERS, catch_response=True)
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
    locust.logger.info(f"key = {project_key}, id = {project_id}, plan = {project_plan}")
    assert f'currentViewConfig\"{{\"id\":{board_id}', f'Could not open board {board_id}'

    locust.client.post('/rest/webResources/1.0/resources', params.body["1"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["2"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["3"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["4"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["5"], TEXT_HEADERS, catch_response=True)

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
    locust.client.post('/rest/webResources/1.0/resources', params.body["6"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', params.body["7"], TEXT_HEADERS, catch_response=True)
    if view_backlog:
        locust.client.get(f'/rest/greenhopper/1.0/rapidviewconfig/editmodel.json?rapidViewId={board_id}'
                          f'&_={timestamp_int()}', catch_response=True)
    if project_key:
        locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited',
                          {"id": f"com.pyxis.greenhopper.jira:project-sidebar-work-{project_plan}"},
                          catch_response=True)
