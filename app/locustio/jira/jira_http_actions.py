from locustio.jira.common_utils import *
import random
import itertools
from locust.exception import ResponseError
import re
import inspect
from locustio.jira.requests_params import *

counter = itertools.count()


@measure
def login_and_view_dashboard(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    user = random.choice(dataset["users"])
    body = LOGIN_BODY
    body['os_username'] = user[0]
    body['os_password'] = user[1]

    locust.client.post('/login.jsp', body, TEXT_HEADERS, catch_response=True)
    r = locust.client.get('/', catch_response=True)
    content = r.content.decode('utf-8')
    locust.client.post("/plugins/servlet/gadgets/dashboard-diagnostics",
                       {"uri": f"{locust.client.base_url.lower()}/secure/Dashboard.jspa"},
                       TEXT_HEADERS, catch_response=True)

    logged_user_pattern = LOGGED_USER.replace('username', user[0])
    # Assertions
    token = re.findall(ATL_TOKEN_PATTERN_LOGIN, content)
    if not token:
        locust.logger.info(f'{content}')
        raise ResponseError(ERR_TOKEN_NOT_FOUND)
    assert logged_user_pattern in content, f'User {user[0]} authentication failed'
    locust.user = user[0]
    locust.atl_token = token[0]
    locust.logger.info(f"User {user[0]} logged in with atl_token: {token[0]}")


@measure
def view_issue(locust):
    func_name = inspect.stack()[0][3]
    issue_key = random.choice(dataset['issues'])[0]
    project_key = random.choice(dataset['issues'])[2]

    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    r = locust.client.get(f'/browse/{issue_key}', catch_response=True)
    content = r.content.decode('utf-8')

    issue_id = re.findall(ISSUE_ID_PATTERN, content)[0]
    project_avatar_id = re.findall(PROJECT_AVATAR_ID_PATTERN, content)[0]
    edit_allowed = re.findall(EDIT_ALLOWED_PATTERN, content)

    locust.client.get(f'/secure/projectavatar?avatarId={project_avatar_id}', catch_response=True)
    # Assertions
    assert_str = ASSERT_ISSUE_KEY.replace('issuekey', issue_key)
    assert assert_str in content, f'Issue {issue_key} not found'
    locust.logger.info(f"Issue {issue_key} is opened successfully")

    locust.logger.info(f'Issue key: {issue_key}, issue_id {issue_id}')
    if edit_allowed:
        url = f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId={issue_id}&_={timestamp_int()}'
        locust.client.get(url, catch_response=True)
    locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited', BROWSE_PROJECT_PAYLOAD,
                      catch_response=True)


@measure
def create_issue(locust):
    func_name = inspect.stack()[0][3]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    r = locust.client.post(OPEN_QUICK_CREATE_URL, ADMIN_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')
    atl_token = re.findall(ATL_TOKEN_PATTERN_CREATE_ISSUE, content)
    form_token = re.findall(FORM_TOKEN_PATTERN, content)
    issue_type = re.findall(ISSUE_TYPE_PATTERN, content)
    project_id = re.findall(PROJECT_ID_PATTERN, content)
    resolution_done = re.findall(RESOLUTION_DONE_PATTERN, content)
    fields_to_retain = re.findall(FIELDS_TO_RETAIN_PATTERN, content)
    custom_fields_to_retain = re.findall(CUSTOM_FIELDS_TO_RETAIN_PATTERN, content)

    issue_body_params_dict = {'atl_token': get_first_index(atl_token, 'atl_token not found'),
                              'form_token': get_first_index(form_token, 'form_token not found'),
                              'issue_type': get_first_index(issue_type, 'issue_type not found'),
                              'project_id': get_first_index(project_id, 'project_id not found'),
                              'resolution_done': get_first_index(resolution_done, 'resolution_done not found'),
                              'fields_to_retain': fields_to_retain,
                              'custom_fields_to_retain': custom_fields_to_retain
                              }

    locust.logger.info(issue_body_params_dict)
    assert ASSERT_STRING_CREATE_ISSUE in content, ERR_CREATE_ISSUE
    locust.client.post('/rest/quickedit/1.0/userpreferences/create', USERPREFERENCES_PAYLOAD,
                       ADMIN_HEADERS, catch_response=True)

    issue_body = prepare_issue_body(issue_body_params_dict, user=locust.user)
    r = locust.client.post('/secure/QuickCreateIssue.jspa?decorator=none', params=issue_body,
                           headers=ADMIN_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')

    assert ASSERT_STRING_CREATE_ISSUE in content, ERR_CREATE_ISSUE
    issue_key = re.findall(CREATED_ISSUE_KEY_PATTERN, content)[0]
    locust.logger.info(f"Issue {issue_key} was successfully created")


@measure
def search_jql(locust):
    func_name = inspect.stack()[0][3]
    resources_body = resources[func_name]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    jql = random.choice(dataset['jqls'])[0]
    r = locust.client.get(f'/issues/?jql={jql}', catch_response=True)
    assert locust.atl_token in r.content.decode('utf-8'), f'Can not search by {jql}'

    # first post resources request
    locust.client.post('/rest/webResources/1.0/resources', resources_body["1"],
                       TEXT_HEADERS, catch_response=True)

    locust.client.get(f'/rest/api/2/filter/favourite?expand=subscriptions[-5:]&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/issueNav/latest/preferredSearchLayout', params={'layoutKey': 'split-view'},
                       headers=NO_TOKEN_HEADERS, catch_response=True)

    # seconds post resources request
    locust.client.post('/rest/webResources/1.0/resources', resources_body["2"],
                       TEXT_HEADERS, catch_response=True)
    r = locust.client.post('/rest/issueNav/1/issueTable', data=PAYLOAD_ISSUE_TABLE,
                           headers=NO_TOKEN_HEADERS, catch_response=True)
    content = r.content.decode('utf-8')
    issue_ids = re.findall(ISSUE_IDS_PATTERN, content)

    # third post resources request
    locust.client.post('/rest/webResources/1.0/resources', resources_body["3"],
                       TEXT_HEADERS, catch_response=True)
    if issue_ids:
        body = prepare_jql_body(issue_ids)
        r = locust.client.post('/rest/issueNav/1/issueTable/stable', data=body,
                               headers=NO_TOKEN_HEADERS, catch_response=True)
        content = r.content.decode('utf-8')
        issue_key = re.findall(SEARCH_JQL_ISSUE_KEY_PATTERN, content)
        if issue_key:
            issue_key = issue_key[0][1]
        issue_id = re.findall(SEARCH_JQL_ISSUE_ID_PATTERN, content)
        if issue_id:
            issue_id = issue_id[0]
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
        if SEARCH_JQL_EDIT_ALLOW in r.content.decode('utf-8'):
            locust.client.get(f'/secure/AjaxIssueEditAction!default.jspa?'
                              f'decorator=none&issueId={issue_id}&_={timestamp_int()}', catch_response=True)


@measure
def view_project_summary(locust):
    func_name = inspect.stack()[0][3]
    resources_body = resources[func_name]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    project_key = random.choice(dataset["issues"])[2]
    r = locust.client.get(f'/projects/{project_key}/summary', catch_response=True)
    content = r.content.decode('utf-8')
    x_st = re.findall(VIEW_PROJECT_SUMMARY_X_ST_PATTERN, content)
    locust.logger.info(f"View project {project_key}")

    assert_string = f'["project-key"]="\\"{project_key}\\"'
    assert assert_string in content, f'{ERR_VIEW_PROJECT_SUMMARY} {project_key}'

    locust.client.post('/rest/webResources/1.0/resources', resources_body["1"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["2"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["3"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=10&relativeLinks=true&streams=key+IS+{project_key}'
                      f'&providers=thirdparty+dvcs-streams-provider+issues&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["4"], TEXT_HEADERS, catch_response=True)
    r = locust.client.get(f'/projects/{project_key}?selectedItem=com.atlassian.jira.jira-projects-plugin:'
                          f'project-activity-summary&decorator=none&contentOnly=true&_={timestamp_int()}',
                          catch_response=True)
    x_st = re.findall(VIEW_PROJECT_SUMMARY_X_ST_PATTERN, r.content.decode('utf-8'))
    locust.client.post('/rest/webResources/1.0/resources', resources_body["5"], TEXT_HEADERS, catch_response=True)
    locust.client.put(f'/rest/api/2/user/properties/lastViewedVignette?username={locust.user}', data={"id": "priority"},
                      headers=TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["6"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/activity-stream/1.0/preferences?_={timestamp_int()}', catch_response=True)
    locust.client.get(f'/plugins/servlet/streams?maxResults=10&relativeLinks=true&streams=key+IS+{project_key}'
                      f'&providers=thirdparty+dvcs-streams-provider+issues&_={timestamp_int()}',
                      catch_response=True)

@measure
def edit_issue(locust):
    func_name = inspect.stack()[0][3]
    resources_body = resources[func_name]
    locust.logger = logging.getLogger(f'{func_name}-%03d' % next(counter))
    issue = random.choice(dataset['issues'])
    issue_id = issue[1]
    issue_key = issue[0]
    project_key = issue[2]
    r = locust.client.get(f'/secure/EditIssue!default.jspa?id={issue_id}', catch_response=True)
    content = r.content.decode('utf-8')

    issue_type = fetch_by_re(EDIT_ISSUE_TYPE_PATTERN, content)
    atl_token = fetch_by_re(EDIT_ISSUE_ATL_TOKEN_PATTERN, content)
    summary = fetch_by_re(EDIT_ISSUE_SUMMARY_PATTERN, content)
    priority = fetch_by_re(EDIT_ISSUE_PRIORITY_PATTERN, content, group_no=2)
    assignee = fetch_by_re(EDIT_ISSUE_ASSIGNEE_REPORTER_PATTERN, content, group_no=2)
    reporter = fetch_by_re(EDIT_ISSUE_REPORTER_PATTERN, content)
    resolution = fetch_by_re(EDIT_ISSUE_RESOLUTION_PATTERN, content)

    assert f' Edit Issue:  [{issue_key}]' in content, f'{ERR_EDIT_ISSUE} - {issue_id}, {issue_key}'
    locust.logger.info(f"Editing issue {issue_key}")

    locust.client.post('/rest/webResources/1.0/resources', resources_body["1"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["2"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["3"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/rest/internal/2/user/mention/search?issueKey={issue_key}'
                      f'&projectKey={project_key}&maxResults=10&_={timestamp_int()}', catch_response=True)

    edit_body = f'id={issue_id}&summary={generate_random_string(15)}&issueType={issue_type}&priority={priority}' \
                f'&dueDate=""&assignee={assignee}&reporter={reporter}&environment=""' \
                f'&description={generate_random_string(500)}&timetracking_originalestimate=""' \
                f'&timetracking_remainingestimate=""&isCreateIssue=""&hasWorkStarted=""&dnd-dropzone=""' \
                f'&comment=""&commentLevel=""&atl_token={atl_token}&Update=Update'
    r = locust.client.post(f'/secure/EditIssue.jspa?atl_token={atl_token}', params=edit_body,
                           headers=TEXT_HEADERS, catch_response=True)
    assert f'[{issue_key}]' in r.content.decode('utf-8')

    locust.client.get(f'/browse/{issue_key}', catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["4"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["5"], TEXT_HEADERS, catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["6"], TEXT_HEADERS, catch_response=True)
    locust.client.get(f'/secure/AjaxIssueEditAction!default.jspa?decorator=none&issueId={issue_id}&_={timestamp_int()}',
                      catch_response=True)
    locust.client.post('/rest/webResources/1.0/resources', resources_body["7"], TEXT_HEADERS, catch_response=True)
    locust.client.put(f'/rest/projects/1.0/project/{project_key}/lastVisited', EDIT_ISSUE_LAST_VISITED_BODY,
                      catch_response=True)

