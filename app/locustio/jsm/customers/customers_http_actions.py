import json
import uuid

import random

from locustio.common_utils import init_logger, jsm_customer_measure, TEXT_HEADERS, RESOURCE_HEADERS, \
    generate_random_string
from locustio.jsm.customers.customers_requests_params import Login, ViewPortal, ViewRequests, ViewRequest, \
    AddComment, ShareRequest, ShareRequestOrg, CreateRequest, jsm_customer_datasets

logger = init_logger(app_type='jsm')
jsm_customer_dataset = jsm_customer_datasets()


@jsm_customer_measure('locust_customer_login_and_view_portals')
def customer_login_and_view_portals(locust):
    session_id = str(uuid.uuid4())
    locust.cross_action_storage[session_id] = dict()
    locust.session_data_storage = locust.cross_action_storage[session_id]
    locust.session_data_storage['app'] = 'jsm'
    locust.session_data_storage['app_type'] = 'customer'

    params = Login()

    user = random.choice(jsm_customer_dataset["customers"])

    customer_requests = user[2:]
    customer_requests_chunks = [customer_requests[x:x + 3] for x in range(0, len(customer_requests), 3)]
    customer_request = random.choice(customer_requests_chunks)

    locust.session_data_storage['request_portal_id'] = customer_request[0]
    locust.session_data_storage['request_id'] = customer_request[1]
    locust.session_data_storage['request_key'] = customer_request[2]

    small_portal = random.choice(jsm_customer_dataset['s_portal'])
    locust.session_data_storage['s_service_desk_id'] = small_portal[0]

    request_types = random.choice(jsm_customer_dataset['request_types'])
    locust.session_data_storage['rt_project_id'] = request_types[0]
    locust.session_data_storage['rt_service_desk_id'] = request_types[1]
    locust.session_data_storage['rt_id'] = request_types[2]

    body = params.login_body
    body['os_username'] = user[0]
    body['os_password'] = user[1]
    locust.session_data_storage['username'] = user[0]
    locust.session_data_storage['password'] = user[1]

    r = locust.post('/servicedesk/customer/user/login', body, TEXT_HEADERS, catch_response=True)

    locust.get('/servicedesk/customer/portals', catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("110"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.post('/rest/servicedesk/1/customer/models', json=params.resources_body.get("115"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("120"),
                headers=RESOURCE_HEADERS, catch_response=True)
    assert '"loginSucceeded":true' in r.content.decode('utf-8'), 'Customer login is failed'


@jsm_customer_measure('locust_customer_view_portal')
def customer_view_portal(locust):
    params = ViewPortal()

    s_service_desk_id = locust.session_data_storage['s_service_desk_id']
    locust.get(f'/servicedesk/customer/portal/{s_service_desk_id}', catch_response=True)
    locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("205"),
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("210"),
                headers=RESOURCE_HEADERS, catch_response=True)


def customer_view_requests(locust):
    params = ViewRequests()
    s_service_desk_id = locust.session_data_storage['s_service_desk_id']

    @jsm_customer_measure('locust_customer_view_requests:my_requests')
    def customer_view_my_requests(locust):
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("250"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        customer_models = {"models": ["user", "organisations", "sharedPortal", "helpCenterBranding", "announcement",
                                      "allReqFilter", "portalWebFragments", "organisations"],
                           "options":
                               {"portalId": s_service_desk_id, "allReqFilter":
                                   {"reporter": "", "status": "open", "portalId": "", "requestTypeId": "", "filter": "",
                                    "selectedPage": 1},
                                "portalWebFragments": {"portalPage": "MY_REQUESTS"}}}
        locust.post('/rest/servicedesk/1/customer/models', json=customer_models, headers=RESOURCE_HEADERS,
                    catch_response=True)
        locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("260"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    @jsm_customer_measure('locust_customer_view_requests:all_requests')
    def customer_view_all_requests(locust):
        locust.post('/rest/webResources/1.0/resources', json=params.resources_body.get("300"),
                    headers=RESOURCE_HEADERS, catch_response=True)
        customer_models = {"models": ["user", "organisations", "sharedPortal", "helpCenterBranding", "announcement",
                                      "allReqFilter", "portalWebFragments", "organisations"],
                           "options": {"portalId": s_service_desk_id,
                                       "allReqFilter": {"reporter": "all", "status": "open", "portalId": "",
                                                        "requestTypeId": "",
                                                        "filter": "", "selectedPage": 1}, "portalWebFragments":
                                       {"portalPage": "MY_REQUESTS"}}}
        locust.post('/rest/servicedesk/1/customer/models', json=customer_models, headers=RESOURCE_HEADERS,
                    catch_response=True)

    @jsm_customer_measure('locust_customer_view_requests:with_filter_requests')
    def customer_view_all_requests_with_filter(locust):
        portal_request_filter = f'*{generate_random_string(1, only_letters=True)}' \
                                f'*{generate_random_string(1, only_letters=True)}*'
        customer_models = {"models": ["user", "organisations", "sharedPortal", "helpCenterBranding", "announcement",
                                      "allReqFilter", "portalWebFragments", "organisations"],
                           "options": {"allReqFilter": {"reporter": "all", "status": "open", "portalId": "",
                                                        "requestTypeId": "", "filter": f"{portal_request_filter}",
                                                        "selectedPage": 1}, "portalWebFragments":
                                                                            {"portalPage": "MY_REQUESTS"}}}
        locust.post('/rest/servicedesk/1/customer/models', json=customer_models, headers=RESOURCE_HEADERS,
                    catch_response=True)
        locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("325"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    customer_view_my_requests(locust)
    customer_view_all_requests(locust)
    customer_view_all_requests_with_filter(locust)


@jsm_customer_measure('locust_customer_view_request')
def customer_view_request(locust):
    params = ViewRequest()
    request_portal_id = locust.session_data_storage['request_portal_id']
    request_key = locust.session_data_storage['request_key']
    customer_models = {"models": ["user", "organisations", "sharedPortal", "helpCenterBranding", "portal", "reqDetails",
                                  "portalWebFragments"],
                       "options": {"portalId": f"{request_portal_id}",
                                   "portal": {"id": f"{request_portal_id}"},
                                   "reqDetails": {"key": f"{request_key}"},
                                   "portalWebFragments": {"portalPage": "VIEW_REQUEST"}}}

    locust.post('/rest/servicedesk/1/customer/models', json=customer_models, headers=RESOURCE_HEADERS,
                catch_response=True)
    locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("355"),
                headers=RESOURCE_HEADERS, catch_response=True)


@jsm_customer_measure('locust_customer_add_comment')
def customer_add_comment(locust):
    params = AddComment()
    p_comment = f'Locust comment {generate_random_string(10)}'
    request_id = locust.session_data_storage['request_id']
    locust.post('/rest/servicedesk/1/servicedesk/customer/comment', json={"fileIds": [], "comment": f"{p_comment}",
                                                                          "issueId": f"{request_id}"},
                headers=RESOURCE_HEADERS, catch_response=True)
    locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("365"),
                headers=RESOURCE_HEADERS, catch_response=True)


def customer_share_request_with_customer(locust):
    params = ShareRequest()
    request_key = locust.session_data_storage['request_key']

    @jsm_customer_measure('locust_customer_share_request_with_customer:search_customer')
    def customer_search_customer_for_share_with(locust):
        r = locust.get(f'/rest/servicedesk/1/customer/participants/{request_key}/search?q=performance_c',
                       catch_response=True)
        text_response = json.loads(r.content)

        # If at least one user was found
        if text_response:
            user_to_share_with = random.choice(text_response)
            locust.session_data_storage['customer_id_share_with'] = user_to_share_with['id']
            locust.session_data_storage['customer_key_share_with'] = user_to_share_with['userKey']

        locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("410"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    @jsm_customer_measure('locust_customer_share_request_with_customer:add_customer')
    def customer_add_customer(locust):
        if locust.session_data_storage['customer_id_share_with']:
            locust.client.put(f'/rest/servicedesk/1/customer/participants/{request_key}/share',
                              json={"usernames": [f"{locust.session_data_storage['customer_id_share_with']}"],
                                    "organisationIds": [], "emails": []},
                              headers=RESOURCE_HEADERS, catch_response=True)

    @jsm_customer_measure('locust_customer_share_request_with_customer:remove_customer')
    def customer_remove_customer(locust):
        if locust.session_data_storage['customer_id_share_with']:
            locust.post(f'/rest/servicedesk/1/servicedesk/customer/participant/removeParticipant/{request_key}',
                        json={"userKey": f"{locust.session_data_storage['customer_key_share_with']}"},
                        headers=RESOURCE_HEADERS, catch_response=True)
        customer_models = params.resources_body.get('460')
        customer_models['options']['portalId'] = locust.session_data_storage['request_portal_id']
        customer_models['options']['portal']['id'] = locust.session_data_storage['request_portal_id']
        customer_models['options']['reqDetails']['key'] = locust.session_data_storage['request_key']
        locust.post('/rest/servicedesk/1/customer/models', json=customer_models, headers=RESOURCE_HEADERS,
                    catch_response=True)

    customer_search_customer_for_share_with(locust)
    customer_add_customer(locust)
    customer_remove_customer(locust)


def customer_share_request_with_org(locust):
    params = ShareRequestOrg()
    request_key = locust.session_data_storage['request_key']

    @jsm_customer_measure('locust_customer_share_request_with_org:search_org')
    def customer_search_org_for_share_with(locust):
        r = locust.get(f'/rest/servicedesk/1/customer/participants/{request_key}/search?q=perf_org',
                       catch_response=True)
        content = json.loads(r.content)
        if content:
            locust.session_data_storage['org_id_share_with'] = random.choice(content)['id']
        locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("510"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    @jsm_customer_measure('locust_customer_share_request_with_org:add_org')
    def customer_add_org(locust):
        if 'org_id_share_with' in locust.session_data_storage:
            locust.client.put(f'/rest/servicedesk/1/customer/participants/{request_key}/share',
                              json={"usernames": [], "organisationIds":
                                                     [f"{locust.session_data_storage['org_id_share_with']}"],
                                    "emails": []},
                              catch_response=True)

    @jsm_customer_measure('locust_customer_share_request_with_org:remove_org')
    def customer_remove_org(locust):
        if 'org_id_share_with' in locust.session_data_storage:
            locust.client.put(f'/rest/servicedesk/1/customer/participants/{request_key}/removeOrganisation',
                              json={"organisationId": locust.session_data_storage['org_id_share_with']},
                              catch_response=True)
        customer_model = {"models": ["user", "organisations", "sharedPortal", "helpCenterBranding", "portal",
                                     "reqDetails", "portalWebFragments"],
                          "options":
                          {"portalId": f"{locust.session_data_storage['request_portal_id']}",
                           "portal": {"id": f"{locust.session_data_storage['request_portal_id']}"},
                           "reqDetails": {"key": f"{request_key}"}, "portalWebFragments":
                                                                    {"portalPage": "VIEW_REQUEST"}}}
        locust.post('/rest/servicedesk/1/customer/models', json=customer_model,
                    headers=RESOURCE_HEADERS, catch_response=True)

    customer_search_org_for_share_with(locust)
    customer_add_org(locust)
    customer_remove_org(locust)


def customer_create_request(locust):
    params = CreateRequest()
    rt_service_desk_id = locust.session_data_storage['rt_service_desk_id']
    rt_id = locust.session_data_storage['rt_id']
    rt_project_id = locust.session_data_storage['rt_project_id']

    @jsm_customer_measure('locust_customer_create_request:open_create_request_view')
    def customer_open_create_request_view(locust):
        customer_model = {"models":
                          ["user", "organisations", "sharedPortal", "portal", "helpCenterBranding", "reqCreate",
                           "portalWebFragments"], "options": {"portalId": f"{rt_service_desk_id}",
                                                              "portal": {"id": f"{rt_service_desk_id}"},
                                                              "reqCreate": {"id": f"{rt_id}"},
                                                              "portalWebFragments": {"portalPage": "CREATE_REQUEST"}}}
        locust.post('/rest/servicedesk/1/customer/models', json=customer_model,
                    headers={"Accept": "*/*", "Content-Type": "application/json"}, catch_response=True)
        locust.post('/rest/analytics/1.0/publish/bulk', json=params.resources_body.get("602"),
                    headers=RESOURCE_HEADERS, catch_response=True)

    @jsm_customer_measure('locust_customer_create_request:create_request')
    def customer_create_request(locust):
        p_summary = f'Locust summary {generate_random_string(10, only_letters=True)}'
        p_description = f'Locust description {generate_random_string(10)}'

        params_create_issue = {"sd-kb-article-viewed": "false", "summary": p_summary, "description": p_description,
                               "pid": rt_project_id, "projectId": rt_project_id}
        TEXT_HEADERS['X-Atlassian-Token'] = 'no-check'
        r = locust.post(f'/servicedesk/customer/portal/{rt_service_desk_id}/create/{rt_id}', params=params_create_issue,
                        headers=TEXT_HEADERS, catch_response=True)

        content = json.loads(r.content)
        locust.session_data_storage['create_issue_key'] = content['issue']['key']
        locust.post('/rest/servicedesk/project-ui/noeyeball/1/welcome-guide/item-completer/completeItem/'
                    'create-request',
                    headers={"Accept": "*/*"}, catch_response=True)

    @jsm_customer_measure('locust_customer_create_request:view_request_after_creation')
    def customer_view_request_after_creation(locust):
        customer_models = {"models": ["user", "organisations", "sharedPortal", "helpCenterBranding", "portal",
                                      "reqDetails", "portalWebFragments"],
                           "options": {"portalId": f"{rt_service_desk_id}",
                                       "portal": {"id": f"{rt_service_desk_id}"},
                                       "reqDetails": {"key": f"{locust.session_data_storage['create_issue_key']}"},
                                       "portalWebFragments": {"portalPage": "VIEW_REQUEST"}}}
        locust.post('/rest/servicedesk/1/customer/models', json=customer_models,
                    headers=RESOURCE_HEADERS, catch_response=True)

    customer_open_create_request_view(locust)
    customer_create_request(locust)
    customer_view_request_after_creation(locust)
