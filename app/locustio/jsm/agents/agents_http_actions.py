import uuid
import random
import json
from locustio.common_utils import init_logger, jsm_agent_measure, TEXT_HEADERS, RESOURCE_HEADERS, timestamp_int, \
    fetch_by_re, generate_random_string
from locustio.jsm.agents.agents_requests_params import Login, AllOpenQueue, BrowseProjects, ViewRequest, AddComment, \
    ViewWorkloadReport, ViewTimeToResolutionReport, ViewReportCreatedVsResolved, ViewCustomers

logger = init_logger(app_type='jsm')


@jsm_agent_measure('locust_agent_login_and_view_dashboard')
def agent_login_and_view_dashboard(locust, jsm_agent_dataset):
    session_id = str(uuid.uuid4())
    locust.cross_action_storage[session_id] = dict()
    locust.session_data_storage = locust.cross_action_storage[session_id]
    locust.session_data_storage['app'] = 'jsm'
    locust.session_data_storage['app_type'] = 'agent'

    params = Login()

    # Define dataset for further actions
    user = random.choice(jsm_agent_dataset["agents"])
    small_project = random.choice(jsm_agent_dataset['s_project'])
    medium_project = None
    if jsm_agent_dataset['m_project']:
        medium_project = random.choice(jsm_agent_dataset['m_project'])
    request = random.choice(jsm_agent_dataset['requests'])

    locust.session_data_storage['request_id'] = request[0]
    locust.session_data_storage['request_key'] = request[1]
    locust.session_data_storage['request_service_desk_id'] = request[2]
    locust.session_data_storage['request_project_id'] = request[3]
    locust.session_data_storage['request_project_key'] = request[4]

    locust.session_data_storage['s_project_id'] = small_project[1]
    locust.session_data_storage['s_project_key'] = small_project[2]
    locust.session_data_storage['s_project_all_open_queue_id'] = small_project[4]
    locust.session_data_storage['s_created_vs_resolved_queue_id'] = small_project[5]
    locust.session_data_storage['s_time_to_resolution_id'] = small_project[6]

    # Medium project dataset definition
    if medium_project:
        locust.session_data_storage['m_project_id'] = medium_project[1]
        locust.session_data_storage['m_project_key'] = medium_project[2]
        locust.session_data_storage['m_project_all_open_queue_id'] = medium_project[4]
        locust.session_data_storage['m_created_vs_resolved_queue_id'] = medium_project[5]
        locust.session_data_storage['m_time_to_resolution_id'] = medium_project[6]

    body = params.login_body
    body['os_username'] = user[0]
    body['os_password'] = user[1]

    legacy_form = False

    # is 2sv login form
    r = locust.get('/login.jsp', catch_response=True)
    if b'login-form-remember-me' in r.content:
        legacy_form = True

    if legacy_form:
        locust.post('/login.jsp', body, TEXT_HEADERS, catch_response=True)
        logger.locust_info(f"Legacy login flow for user {user[0]}")
    else:
        logger.locust_info(f"2SV login flow for user {user[0]}")

        login_body = {'username': user[0],
                      'password': user[1],
                      'rememberMe': 'True',
                      'targetUrl': ''
                      }

        headers = {
            "Content-Type": "application/json"
        }

        # 15 /rest/tsv/1.0/authenticate
        locust.post('/rest/tsv/1.0/authenticate',
                    json=login_body,
                    headers=headers,
                    catch_response=True)

    r = locust.get('/', catch_response=True)
    if not r.content:
        raise Exception('Please check server hostname in jsm.yml file')
    content = r.content.decode('utf-8')

    locust.post("/plugins/servlet/gadgets/dashboard-diagnostics",
                {"uri": f"{locust.client.base_url.lower()}/secure/Dashboard.jspa"},
                TEXT_HEADERS, catch_response=True)
    locust.get(
        f'/rest/gadget/1.0/issueTable/jql?num=10&tableContext=jira.table.cols.dashboard'
        f'&addDefault=true&enableSorting=true&paging=true&showActions=true'
        f'&jql=assignee+%3D+currentUser()+AND'
        f'+resolution+%3D+unresolved+ORDER+BY+priority+DESC%2C+created+ASC'
        f'&sortBy=&startIndex=0&_={timestamp_int()}', catch_response=True)
    # Assertions
    token = fetch_by_re(params.atl_token_pattern, content)
    if not (f'title="loggedInUser" value="{user[0]}">' in content):
        logger.error(f'User {user[0]} authentication failed: {content}')
    assert f'title="loggedInUser" value="{user[0]}">' in content, 'User authentication failed'

    locust.session_data_storage['username'] = user[0]
    locust.session_data_storage['password'] = user[1]
    locust.session_data_storage["token"] = token
    logger.locust_info(
        f"{params.action_name}: User {user[0]} logged in with atl_token: {token}")


@jsm_agent_measure('locust_agent_view_queues_small:all_open_queue')
def agent_view_queue_all_open_small(locust):
    view_project_queue(
        locust=locust,
        project_key=locust.session_data_storage['s_project_key'],
        project_id=locust.session_data_storage['s_project_id'],
        queue_id=locust.session_data_storage['s_project_all_open_queue_id'])


@jsm_agent_measure('locust_agent_view_queues_small:random_queue')
def agent_view_queue_random_small(locust):
    small_project_key = locust.session_data_storage['s_project_key']
    small_project_id = locust.session_data_storage['s_project_id']
    random_queue_id = locust.session_data_storage[f'{small_project_key}_random_queue_id']
    view_project_queue(locust=locust, project_key=small_project_key,
                       project_id=small_project_id, queue_id=random_queue_id)


@jsm_agent_measure('locust_agent_view_queues_medium:all_open_queue')
def agent_view_queue_all_open_medium(locust):
    view_project_queue(
        locust=locust,
        project_key=locust.session_data_storage['m_project_key'],
        project_id=locust.session_data_storage['m_project_id'],
        queue_id=locust.session_data_storage['m_project_all_open_queue_id'])


@jsm_agent_measure('locust_agent_view_queues_medium:random_queue')
def agent_view_queue_random_medium(locust):
    medium_project_key = locust.session_data_storage['m_project_key']
    medium_project_id = locust.session_data_storage['m_project_id']
    random_queue_id = locust.session_data_storage[f'{medium_project_key}_random_queue_id']
    view_project_queue(locust=locust, project_key=medium_project_key,
                       project_id=medium_project_id, queue_id=random_queue_id)


@jsm_agent_measure('locust_agent_browse_projects')
def agent_browse_projects(locust):
    params = BrowseProjects()
    locust.get(
        '/secure/BrowseProjects.jspa?selectedCategory=all&selectedProjectType=service_desk',
        catch_response=True)


@jsm_agent_measure('locust_agent_view_request')
def agent_view_request(locust):
    params = ViewRequest()
    locust.get(
        f'/browse/{locust.session_data_storage["request_key"]}',
        catch_response=True)


def agent_add_comment(locust):
    params = AddComment()

    @jsm_agent_measure('locust_agent_add_comment:open_request_comment')
    def agent_open_request_comment(locust):
        locust.get(
            f'/rest/servicedesk/canned-responses/1/search/{locust.session_data_storage["request_project_key"]}?'
            f'issueKey={locust.session_data_storage["request_key"]}&'
            f'limitUsagesToUser=true&'
            f'limit=5&'
            f'daysSince=30&'
            f'substitute=true&'
            f'_{timestamp_int()}',
            catch_response=True)
        locust.get(
            f'/rest/servicedesk/canned-responses/1/search/{locust.session_data_storage["request_project_key"]}?'
            f'issueKey={locust.session_data_storage["request_key"]}&'
            f'limit=5&'
            f'substitute=true&'
            f'_{timestamp_int()}',
            catch_response=True)

    @jsm_agent_measure('locust_agent_add_comment:save_request_comment')
    def agent_save_request_comment(locust):
        comment = f'Locust comment {generate_random_string(10)}'
        body = {"body": f"{comment}", "properties": [
            {"key": "sd.public.comment", "value": {"internal": True}}]}
        locust.post(
            f'/rest/api/2/issue/{locust.session_data_storage["request_id"]}/comment',
            headers=RESOURCE_HEADERS,
            json=body,
            catch_response=True)

        TEXT_HEADERS['X-SITEMESH-OFF'] = 'true'
        locust.post(
            '/secure/AjaxIssueAction!default.jspa',
            params={
                "decorator": None,
                "issueKey": locust.session_data_storage["request_id"],
                "prefetch": False,
                "shouldUpdateCurrentProject": True},
            headers=TEXT_HEADERS,
            catch_response=True)

        locust.get(
            f'/rest/servicedesk/canned-responses/1/search/{locust.session_data_storage["request_project_key"]}'
            f'?issueKey={locust.session_data_storage["request_key"]}&'
            f'limitUsagesToUser=true&limit=5&daysSince=30&substitute=true&_={timestamp_int()}',
            catch_response=True)
        locust.get(
            f'/rest/servicedesk/canned-responses/1/search/{locust.session_data_storage["request_project_key"]}'
            f'?issueKey={locust.session_data_storage["request_key"]}&'
            f'limit=5&substitute=true&_={timestamp_int()}', catch_response=True)

    agent_open_request_comment(locust)
    agent_save_request_comment(locust)


@jsm_agent_measure('locust_agent_view_report_workload_small')
def agent_view_report_workload_small(locust):
    small_project_id = locust.session_data_storage['s_project_id']
    small_project_key = locust.session_data_storage['s_project_key']
    view_workload_report(
        locust=locust,
        project_id=small_project_id,
        project_key=small_project_key)


@jsm_agent_measure('locust_agent_view_report_workload_medium')
def agent_view_report_workload_medium(locust):
    medium_project_id = locust.session_data_storage['m_project_id']
    medium_project_key = locust.session_data_storage['m_project_key']
    view_workload_report(
        locust=locust,
        project_id=medium_project_id,
        project_key=medium_project_key)


@jsm_agent_measure('locust_agent_view_report_created_vs_resolved_small')
def agent_view_report_created_vs_resolved_small(locust):
    created_vs_resolved_id = locust.session_data_storage['s_created_vs_resolved_queue_id']
    small_project_key = locust.session_data_storage['s_project_key']
    view_created_vs_resolved_report(
        locust=locust,
        project_key=small_project_key,
        created_vs_resolved_id=created_vs_resolved_id)


@jsm_agent_measure('locust_agent_view_report_created_vs_resolved_medium')
def agent_view_report_created_vs_resolved_medium(locust):
    created_vs_resolved_id = locust.session_data_storage['m_created_vs_resolved_queue_id']
    medium_project_key = locust.session_data_storage['m_project_key']
    view_created_vs_resolved_report(
        locust=locust,
        project_key=medium_project_key,
        created_vs_resolved_id=created_vs_resolved_id)


@jsm_agent_measure('locust_agent_view_customers')
def agent_view_customers(locust):
    params = ViewCustomers()
    small_project_key = locust.session_data_storage['s_project_key']
    locust.get(f'/projects/{small_project_key}/customers', catch_response=True)
    locust.client.put(
        f'/rest/projects/1.0/project/{small_project_key}/lastVisited',
        params.last_visited_body,
        catch_response=True)
    locust.get(
        f'/rest/servicedesk/1/pages/people/customers/pagination/{small_project_key}',
        catch_response=True)
    locust.get(
        f'/rest/servicedesk/1/pages/people/customers/pagination/{small_project_key}/search?query=&page=1',
        catch_response=True)


def view_project_queue(locust, project_key, project_id, queue_id):
    params = AllOpenQueue()
    locust.get(
        f'/projects/{project_key}/queues/custom/{queue_id}',
        catch_response=True)

    locust.client.put(
        f'/rest/projects/1.0/project/{project_key}/lastVisited',
        params.last_visited_project_body,
        catch_response=True)
    locust.get(f'/rest/projects/1.0/subnav/sd-queues-nav?_={timestamp_int()}',
               catch_response=True)

    r = locust.post(
        f'/rest/servicedesk/1/{project_key}/webfragments/sections/sd-queues-nav,servicedesk.agent.'
        f'queues,servicedesk.agent.queues.ungrouped',
        headers=RESOURCE_HEADERS,
        json={
            "projectKey": f"{project_key}"},
        catch_response=True)

    queues_info = json.loads(r.content)
    queues_ids = []
    items = [queue['items'] for queue in queues_info]

    for item in items:
        if item:
            for queue in item:
                if queue['label'] not in [
                    'All open',
                    'Recently resolved',
                        'Resolved past 7 days'] and queue['params']['count'] != '0':
                    queues_ids.append(queue['key'])

    # Set small project random queue id for action 'view_queue_random'
    locust.session_data_storage[f'{project_key}_random_queue_id'] = random.choice(
        queues_ids)

    locust.client.put(
        '/rest/projects/1.0/subnav/sd-queues-nav/pin',
        headers=RESOURCE_HEADERS,
        catch_response=True)
    locust.get(
        f'/rest/servicedesk/1/servicedesk/{project_key}/queues/page?_={timestamp_int()}',
        catch_response=True)
    locust.get(
        f'/rest/servicedesk/1/servicedesk/{project_key}/queues/queues-limit?_={timestamp_int()}',
        catch_response=True)

    locust.get(
        f"/rest/servicedesk/1/servicedesk/{project_key}/issuelist?asc=false&excludeLinkedToMajorIncidents="
        f"false&startIndex=0&columnNames=duedate&jql=project+%3D+{project_key}+AND+resolution+%3D+Unresolved+"
        f"ORDER+BY+%22Time+to+resolution%22+ASC&issuesPerPage=50&orderBy=", catch_response=True)

    locust.get(
        f'/rest/servicedesk/1/servicedesk/{project_key}/queues/poll?projectStateHash=undefined?_'
        f'={timestamp_int()}',
        catch_response=True)

    locust.post(
        f'/rest/servicedesk/1/{project_key}/webfragments/sections/sd-queues-nav,servicedesk.agent.'
        f'queues,servicedesk.agent.queues.ungrouped',
        headers=RESOURCE_HEADERS,
        json={
            "projectKey": f"{project_key}"},
        catch_response=True)
    locust.get(
        f"/rest/servicedesk/1/servicedesk/{project_key}/issuelist/updated?asc=false"
        f"&excludeLinkedToMajorIncidents=false&currentIssueHash=f28505024e00a8d3cc3a408bffacba4d44803233"
        f"&startIndex=0&columnNames=duedate"
        f"&jql=project+%3D+{project_key}+AND+resolution+%3D+Unresolved+"
        f"ORDER+BY+%22Time+to+resolution%22+ASC&issuesPerPage=50&orderBy=",
        catch_response=True)
    locust.client.put(
        '/rest/projects/1.0/subnav/sd-queues-nav/pin',
        headers=RESOURCE_HEADERS,
        catch_response=True)


def view_workload_report(locust, project_key, project_id):
    params = ViewWorkloadReport()
    locust.get(
        f'/projects/{project_key}/reports/workload',
        catch_response=True)

    locust.get(
        f'/rest/servicedesk/1/servicedesk/{project_key}/precondition?_{timestamp_int()}',
        catch_response=True)
    locust.get(
        f'/rest/servicedesk/1/servicedesk/{project_key}/warnings?_{timestamp_int()}',
        catch_response=True)

    locust.client.put(
        f'/rest/projects/1.0/project/{project_key}/lastVisited',
        params.last_visited_project_body,
        catch_response=True)

    locust.post(
        f'/rest/servicedesk/1/{project_key}/webfragments/sections/sd-reports-nav,'
        f'servicedesk.agent.reports,servicedesk.agent.reports.ungrouped,sd-reports-nav-custom-section',
        json={
            "projectKey": project_key},
        catch_response=True)

    locust.get(
        f'/rest/servicedesk/1/pages/people/agents/{project_key}/search?_query=&_={timestamp_int()}',
        catch_response=True)


def view_time_to_resolution_report(locust, project_key, time_to_resolution_id):
    params = ViewTimeToResolutionReport()
    locust.get(
        f'/projects/{project_key}/reports/custom/{time_to_resolution_id}/timescale/2',
        catch_response=True)
    locust.client.put(
        f'/rest/projects/1.0/project/{project_key}/lastVisited',
        params.last_visited_body,
        catch_response=True)
    locust.get(f'/rest/projects/1.0/subnav/sd-reports-nav?_={timestamp_int()}',
               catch_response=True)

    locust.post(
        f'/rest/servicedesk/1/{project_key}/webfragments/sections/sd-reports-nav,servicedesk.agent.reports,'
        f'servicedesk.agent.reports.ungrouped,sd-reports-nav-custom-section',
        json={
            "projectKey": project_key},
        catch_response=True)
    locust.get(
        f'/rest/servicedesk/reports/1/servicedesk/{project_key}/report/{time_to_resolution_id}?'
        f'timescaleId=2&_={timestamp_int()}',
        catch_response=True)


def view_created_vs_resolved_report(
        locust,
        project_key,
        created_vs_resolved_id):
    params = ViewReportCreatedVsResolved()
    locust.get(
        f'/projects/{project_key}/reports/custom/{created_vs_resolved_id}/timescale/2',
        catch_response=True)
    locust.client.put(
        f'/rest/projects/1.0/project/{project_key}/lastVisited',
        params.last_visited_body,
        catch_response=True)
    locust.get(f'/rest/projects/1.0/subnav/sd-reports-nav?_={timestamp_int()}',
               catch_response=True)
    locust.post(
        f'/rest/servicedesk/1/{project_key}/webfragments/sections/sd-reports-nav,servicedesk.agent.reports,'
        f'servicedesk.agent.reports.ungrouped,sd-reports-nav-custom-section',
        json={
            "projectKey": project_key},
        catch_response=True)
    locust.get(
        f'/rest/servicedesk/reports/1/servicedesk/{project_key}/report/{created_vs_resolved_id}',
        catch_response=True)
