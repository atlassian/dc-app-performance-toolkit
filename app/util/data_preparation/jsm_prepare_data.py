import random

from concurrent.futures.thread import ThreadPoolExecutor
from itertools import repeat
from prepare_data_common import __write_to_file, __generate_random_string, __warnings_filter
from util.api.abstract_clients import JSM_EXPERIMENTAL_HEADERS
from util.api.jira_clients import JiraRestClient
from util.api.jsm_clients import JsmRestClient
from util.common_util import print_timing
from util.conf import JSM_SETTINGS
from util.project_paths import JSM_DATASET_AGENTS, JSM_DATASET_CUSTOMERS, JSM_DATASET_REQUESTS, \
    JSM_DATASET_SERVICE_DESKS_L, JSM_DATASET_SERVICE_DESKS_M, JSM_DATASET_SERVICE_DESKS_S, JSM_DATASET_REQUEST_TYPES, \
    JSM_DATASET_CUSTOM_ISSUES, JSM_DATASET_INSIGHT_ISSUES, JSM_DATASET_INSIGHT_SCHEMAS

__warnings_filter()

MAX_WORKERS = None

ERROR_LIMIT = 10
DEFAULT_AGENT_PREFIX = 'performance_agent_'
DEFAULT_AGENT_APP_KEYS = ["jira-servicedesk"]
DEFAULT_CUSTOMER_PREFIX = 'performance_customer_'
DEFAULT_PASSWORD = 'password'
DEFAULT_ORGANIZATION = 'perf_organization'

AGENTS = "agents"
CUSTOMERS = "customers"
REQUESTS = "requests"
SERVICE_DESKS_LARGE = "service_desks_large"
SERVICE_DESKS_MEDIUM = "service_desks_medium"
SERVICE_DESKS_SMALL = "service_desks_small"
REQUEST_TYPES = "request_types"
CUSTOM_ISSUES = "custom_issues"
INSIGHT_ISSUES = "insight_issues"
INSIGHT_SCHEMAS = "insight_schemas"
# Issues to retrieve per project in percentage. E.g. retrieve 35% of issues from first project, 20% from second, etc.
# Retrieving 5% of all issues from projects 10-last project.
PROJECTS_ISSUES_PERC = {1: 35, 2: 20, 3: 15, 4: 5, 5: 5, 6: 5, 7: 2, 8: 2, 9: 2, 10: 2}
TOTAL_ISSUES_TO_RETRIEVE = 8000
LARGE_SERVICE_DESK_TRIGGER = 100000  # Count of requests per "large" service desk.
MEDIUM_SERVICE_DESK_TRIGGER = 10000  # Count of requests per "medium" service desk.
NUMBER_OF_REQUESTS_PER_CUSTOMER = 50
REQUEST_TYPES_NAMES = ['Technical support', 'Licensing and billing questions', 'Onboard new employees',
                       'Travel request', 'Product trial questions', 'Set up VPN to the office', 'Suggest a new feature',
                       'Fix an account problem', 'Request admin access', 'Purchase over $100',
                       'Get a guest wifi account', 'Set up a phone line redirect', 'Suggest improvement',
                       'Get IT help', 'Other questions']

performance_agents_count = JSM_SETTINGS.agents_concurrency
performance_customers_count = JSM_SETTINGS.customers_concurrency


def __calculate_issues_per_project(projects_count):
    calculated_issues_per_project_count = {}
    max_percentage_key = max(PROJECTS_ISSUES_PERC, key=int)
    if projects_count > max_percentage_key:
        percent_for_other_projects = round((100 - sum(PROJECTS_ISSUES_PERC.values())) /
                                           (projects_count - max(PROJECTS_ISSUES_PERC, key=int)), 3)
        calculated_issues_percentage = PROJECTS_ISSUES_PERC
    else:
        percent_for_other_projects = 0
        # TODO resolve Unexpected types warning from pycharm
        calculated_issues_percentage = dict(list(PROJECTS_ISSUES_PERC.items())[:projects_count])

    for key, value in calculated_issues_percentage.items():
        calculated_issues_per_project_count[key] = value * TOTAL_ISSUES_TO_RETRIEVE // 100 or 1
    for project_index in range(1, projects_count + 1):
        if project_index not in calculated_issues_per_project_count.keys():
            calculated_issues_per_project_count[project_index] = \
                int(percent_for_other_projects * TOTAL_ISSUES_TO_RETRIEVE // 100 or 1)

    return calculated_issues_per_project_count


def __filter_customer_with_requests(customer, jsm_client):
    customer_auth = (customer['name'], DEFAULT_PASSWORD)
    customer_requests = jsm_client.get_requests(auth=customer_auth, status="OPEN_REQUESTS")
    non_closed_requests = [request for request in customer_requests if request['currentStatus']['status'] != 'Closed']
    customer_dict = {'name': customer['name'], 'has_requests': False}
    if non_closed_requests:
        customer_dict['has_requests'] = True
        requests = []
        random_non_closed_requests = random.sample(non_closed_requests, NUMBER_OF_REQUESTS_PER_CUSTOMER) \
            if len(non_closed_requests) > NUMBER_OF_REQUESTS_PER_CUSTOMER else non_closed_requests
        for request in random_non_closed_requests:
            requests.append((request['serviceDeskId'], request['issueId'], request['issueKey']))
        customer_dict['requests'] = requests
    return customer_dict


def __get_customers_with_requests(jira_client, jsm_client, count):
    customers_with_requests = []
    customers_without_requests = []
    start_at = 0
    max_count_iteration = 1000
    customers_chunk_size = 150
    while len(customers_with_requests) < count:
        customers = jira_client.get_users(username=DEFAULT_CUSTOMER_PREFIX, max_results=max_count_iteration,
                                          start_at=start_at)
        if not customers:
            break
        start_at = start_at + max_count_iteration
        customer_chunks = [customers[x:x + customers_chunk_size]
                           for x in range(0, len(customers), customers_chunk_size)]

        for customer_chunk in customer_chunks:
            if len(customers_with_requests) >= count:
                break

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                customers_datas = list(executor.map(__filter_customer_with_requests, [i for i in customer_chunk],
                                                    repeat(jsm_client)))

            for customer_data in customers_datas:
                if customer_data['has_requests']:
                    if len(customers_with_requests) >= count:
                        break
                    customers_with_requests.append(customer_data)
                else:
                    customers_without_requests.append(customer_data)

    print(f'Retrieved customers with requests: {len(customers_with_requests)}')

    return customers_with_requests


@print_timing('Retrieving agents')
def __get_agents(jira_client):
    prefix_name, application_keys, count = DEFAULT_AGENT_PREFIX, DEFAULT_AGENT_APP_KEYS, performance_agents_count
    perf_users = jira_client.get_users(username=prefix_name, max_results=count)
    users_to_create = count - len(perf_users)
    if users_to_create > 0:
        add_users = __generate_users(api=jira_client, num_to_create=users_to_create, prefix_name=prefix_name,
                                     application_keys=application_keys)
        if not add_users:
            raise Exception(f"ERROR: Jira Service Management could not create agent"
                            f"There were {len(perf_users)}/{count} retrieved.")
        perf_users.extend(add_users)
    return perf_users


@print_timing('Retrieving customers')
def __get_customers(jira_client, jsm_client, servicedesks):
    created_agents = []
    errors_count = 0
    prefix_name, application_keys, count = DEFAULT_CUSTOMER_PREFIX, None, performance_customers_count
    perf_users_with_requests = __get_customers_with_requests(jsm_client=jsm_client, jira_client=jira_client,
                                                             count=count)
    while len(perf_users_with_requests) < performance_customers_count:
        username = f"{prefix_name}{__generate_random_string(10)}"
        try:
            agent = jira_client.create_user(name=username, password=DEFAULT_PASSWORD,
                                            application_keys=application_keys)
            created_agents.append(agent)
            request_types = __get_request_types(jsm_client, servicedesks)
            if not request_types:
                raise Exception("No request types found for service desk")
            random_request_type = random.choice(request_types).split(",")
            service_desk_id = random_request_type[1]
            request_type_id = random_request_type[2]
            # Create the request on behalf of the newly created customer
            jsm_client.create_request(service_desk_id=int(service_desk_id), request_type_id=int(request_type_id),
                                      raise_on_behalf_of=username)
        except Exception as error:
            print(f"WARNING: Create Jira user error: {error}. Retry limits {errors_count}/{ERROR_LIMIT}")
            errors_count = errors_count + 1

    customers_list = []
    for customer in perf_users_with_requests:
        default_customer = f'{customer["name"]},{DEFAULT_PASSWORD}'
        if 'requests' in customer.keys():
            default_customer = f"{default_customer},{','.join([','.join(i) for i in customer['requests']])}"
            customers_list.append(default_customer)
        else:
            customers_list.append(default_customer)
    return customers_list


def __generate_users(api, num_to_create, application_keys, prefix_name):
    errors_count = 0
    created_agents = []
    while len(created_agents) < num_to_create:
        if errors_count >= ERROR_LIMIT:
            raise Exception(f'ERROR: Maximum error limit reached {errors_count}/{ERROR_LIMIT}. '
                            f'Please check the errors in bzt.log')
        username = f"{prefix_name}{__generate_random_string(10)}"
        try:
            agent = api.create_user(name=username, password=DEFAULT_PASSWORD,
                                    application_keys=application_keys)
            created_agents.append(agent)
        except Exception as error:
            print(f"WARNING: Create Jira user error: {error}. Retry limits {errors_count}/{ERROR_LIMIT}")
            errors_count = errors_count + 1
    return created_agents


def __get_service_desk_info(jira_api, jsm_api, service_desk):
    service_desk_requests_count = str(jira_api.get_total_issues_count(f'project = {service_desk["projectKey"]}'))
    service_desk_queues = jsm_api.get_queue(service_desk_id=service_desk['id'])
    service_desk_reports = __get_service_desk_reports(jsm_api, service_desk)

    all_open_queue_id = [queue['id'] for queue in service_desk_queues if queue['name'] == 'All open']
    if not all_open_queue_id:
        raise Exception(f'ERROR: Service Desk with id {service_desk} does not have "All open" queue')
    all_open_queue_id = ''.join(all_open_queue_id)
    service_desk['total_requests'] = service_desk_requests_count
    service_desk['all_open_queue_id'] = all_open_queue_id
    service_desk['created_vs_resolved_id'] = service_desk_reports['created_vs_resolved_id']
    service_desk['time_to_resolution_id'] = service_desk_reports['time_to_resolution_id']
    return service_desk


@print_timing('Preparing service desks')
def __get_service_desks(jsm_api, jira_api, service_desks):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        service_desks_with_requests = list(executor.map(__get_service_desk_info, repeat(jira_api), repeat(jsm_api),
                                                        [service_desk for service_desk in service_desks]))

    print(f"Retrieved {len(service_desks)} Jira Service Desks")
    large_service_desks = []
    medium_service_desks = []
    small_service_desks = []
    for service_desk in service_desks_with_requests:
        if int(service_desk['total_requests']) >= LARGE_SERVICE_DESK_TRIGGER:
            large_service_desks.append(service_desk)
        elif MEDIUM_SERVICE_DESK_TRIGGER <= int(service_desk['total_requests']) < LARGE_SERVICE_DESK_TRIGGER:
            medium_service_desks.append(service_desk)
        elif int(service_desk['total_requests']) < MEDIUM_SERVICE_DESK_TRIGGER:
            small_service_desks.append(service_desk)

    service_desks_list_large = [','.join((service_desk["id"],
                                          service_desk["projectId"],
                                          service_desk["projectKey"],
                                          service_desk["total_requests"],
                                          service_desk["all_open_queue_id"],
                                          service_desk["created_vs_resolved_id"],
                                          service_desk["time_to_resolution_id"]
                                          )) for service_desk in large_service_desks]

    service_desks_list_medium = [','.join((service_desk["id"],
                                           service_desk["projectId"],
                                           service_desk["projectKey"],
                                           service_desk["total_requests"],
                                           service_desk["all_open_queue_id"],
                                           service_desk["created_vs_resolved_id"],
                                           service_desk["time_to_resolution_id"]
                                           )) for service_desk in medium_service_desks]

    service_desks_list_small = [','.join((service_desk["id"],
                                          service_desk["projectId"],
                                          service_desk["projectKey"],
                                          service_desk["total_requests"],
                                          service_desk["all_open_queue_id"],
                                          service_desk["created_vs_resolved_id"],
                                          service_desk["time_to_resolution_id"]
                                          )) for service_desk in small_service_desks]
    return service_desks_list_large, service_desks_list_medium, service_desks_list_small


def __get_service_desk_requests(jira_api, issues_distribution_id, service_desk):
    issues = jira_api.issues_search(jql=f'project = {service_desk["projectKey"]}',
                                    max_results=issues_distribution_id[service_desk['projectKey']])
    distribution_success = len(issues) >= issues_distribution_id[service_desk['projectKey']]
    issues_per_project_list = [','.join((issue['id'],
                                         issue['key'],
                                         service_desk['serviceDeskId'],
                                         service_desk['projectId'],
                                         service_desk['projectKey'],
                                         )) for issue in issues]
    distribution = dict()
    distribution['issues'] = issues_per_project_list
    distribution['distribution_success'] = distribution_success
    distribution['projectKey'] = service_desk['projectKey']
    return distribution


@print_timing('Preparing customers requests')
def __get_requests(jira_api, service_desks, requests_without_distribution):
    # TODO refactor this function (var names, simplify logic)
    service_desks_issues = []
    for service_desk in service_desks:
        service_desk_dict = dict()
        service_desk_dict['serviceDeskId'] = service_desk['id']
        service_desk_dict['projectId'] = service_desk['projectId']
        service_desk_dict['projectKey'] = service_desk['projectKey']
        service_desks_issues.append(service_desk_dict)

    issues_distribution_perc = __calculate_issues_per_project(len(service_desks))
    issues_distribution_id = {}
    for key, value in issues_distribution_perc.items():
        issues_distribution_id[service_desks_issues[key - 1]['projectKey']] = value

    print(f'Start retrieving issues by distribution per project: {issues_distribution_id}')
    distribution_success = True

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        issues_list = list(executor.map(__get_service_desk_requests, repeat(jira_api), repeat(issues_distribution_id),
                                        [issue for issue in service_desks_issues]))

    # Check if requests distribution per service desk is success
    for service_desk in issues_list:
        if not service_desk['distribution_success']:
            distribution_success = False
            print(f'Project {service_desk["projectKey"]} does not have enough requests '
                  f'{len(service_desk["issues"])}/{issues_distribution_id[service_desk["projectKey"]]}')

    if distribution_success:
        requests_list = [issue['issues'] for issue in issues_list]
        requests = sum(requests_list, [])
        print(f'Issues retrieving by distribution per project finished successfully. '
              f'Retrieved {len(requests)} issues')

        return requests

    print(f'Force retrieving {TOTAL_ISSUES_TO_RETRIEVE} issues from Service Desk projects')
    issues_list = []
    for request in requests_without_distribution:
        for service_desk in service_desks_issues:
            if service_desk['projectKey'] in request['key']:
                issue_str = f'{request["id"]},' \
                            f'{request["key"]},' \
                            f'{service_desk["serviceDeskId"]},' \
                            f'{service_desk["projectId"]},' \
                            f'{service_desk["projectKey"]}'

                issues_list.append(issue_str)
    if not issues_list:
        raise Exception("ERROR: Jira Service Management instance does not have any requests.")
    print(f"Force retrieved {len(issues_list)} issues.")
    return issues_list


def __get_service_desk_reports(jsm_api, service_desk):
    service_desk_reports = jsm_api.get_service_desk_reports(project_key=service_desk['projectKey'])
    reports_ids = {}
    for report in service_desk_reports:
        # Implemented in dict to save the order reports of ID's
        if report['label'] == 'Created vs Resolved':
            reports_ids['created_vs_resolved_id'] = report['params']['entityId']
        elif report['label'] == 'Time to resolution':
            reports_ids['time_to_resolution_id'] = report['params']['entityId']
    return reports_ids


def __get_service_desk_request_types(jsm_api, service_desk):
    requests_ids = []
    service_desk_requests = jsm_api.get_request_types(service_desk['id'])
    for desk_req in service_desk_requests:
        requests_ids.append({'service_desk_id': service_desk['id'], 'request_type_id': desk_req['id'],
                             'request_type_name': desk_req['name'], 'project_id': service_desk['projectId']})
    return requests_ids


@print_timing("Preparing request types")
def __get_request_types(jsm_api, service_desks):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        requests_ids = list(executor.map(__get_service_desk_request_types, repeat(jsm_api),
                                         [service_desk for service_desk in service_desks]))

    requests_ids = sum(requests_ids, [])
    request_types_list = []
    for request_id in requests_ids:
        if request_id['request_type_name'] in REQUEST_TYPES_NAMES:
            request_types_list.append([request_id['project_id'],
                                       request_id['service_desk_id'],
                                       request_id['request_type_id']])
    return [','.join(i) for i in request_types_list]


@print_timing("Preparing Insight Schemas")
def __get_insight_schemas(jsm_api):
    insight_schemas = jsm_api.get_all_schemas()
    if not insight_schemas:
        raise Exception('ERROR: Jira Service Management instance does not have any Insight schemas')
    return insight_schemas


@print_timing("Preparing custom issues")
def __get_custom_issues(jira_api, jsm_api, custom_jql):
    issues = []
    if custom_jql:
        issues = jira_api.issues_search(
            jql=custom_jql, max_results=8000
        )
    for issue in issues:
        expanded_issue = jsm_api.get_request(issue_id_or_key=issue['key'])
        issue['service_desk_id'] = expanded_issue['serviceDeskId']
    if not issues:
        print(f"There are no issues found using JQL {custom_jql}")
    return issues


@print_timing("Preparing Insight issues")
def __get_insight_issues(jira_api):
    jql = "Insight is NOT EMPTY"
    issues = jira_api.issues_search(jql=jql, max_results=500)
    if not issues:
        raise Exception('ERROR: Jira Service Management instance does not have any Insight issues')
    return issues


@print_timing("Getting all service desks")
def __get_all_service_desks_and_validate(jira_api, jsm_client):
    all_service_desks = jsm_client.get_all_service_desks()
    if not all_service_desks:
        raise Exception('ERROR: There were no Jira Service Desks found')
    try:
        issues_with_insight = jira_api.issues_search(jql='Insight is not EMPTY', max_results=10000)
    except Exception as e:
        print(f'There were no Insight issues found. {e}')

        issues_with_insight = []
    project_keys_with_insight = [f"{service_desk_issues['key'].split('-')[0]}"
                                 for service_desk_issues
                                 in issues_with_insight]
    if JSM_SETTINGS.insight:
        # service desks with insight issues
        service_desks = [service_desk for service_desk in all_service_desks if service_desk["projectKey"]
                         in project_keys_with_insight]
    else:
        # without insight issues
        service_desks = [service_desk for service_desk in all_service_desks if service_desk["projectKey"]
                         not in project_keys_with_insight]
    if len(service_desks) < 2:
        if JSM_SETTINGS.insight:
            raise Exception('ERROR: At least 2 service desks with Insight issues are needed')
        raise Exception('ERROR: At least 2 service desks are needed')
    return service_desks


@print_timing("Searching issues by project keys")
def __get_issues_by_project_keys(jira_client, jsm_client, project_keys):
    organizations = jsm_client.get_all_organizations()
    perf_organizations = [org for org in organizations if DEFAULT_ORGANIZATION in org['name']]
    perf_organizations_with_users = []
    for org in perf_organizations:
        users_in_org = jsm_client.get_all_users_in_organization(org['id'])
        for user in users_in_org:
            if DEFAULT_CUSTOMER_PREFIX in user['name']:
                perf_organizations_with_users.append(org)
                break

    if not perf_organizations_with_users:
        raise Exception(f'ERROR: There were no organizations found with prefix "{DEFAULT_ORGANIZATION}". '
                        f'Make sure JSM projects has organizations with prefix "{DEFAULT_ORGANIZATION}". '
                        f'Organizations "{DEFAULT_ORGANIZATION}" should have customers'
                        f' with prefix "{DEFAULT_CUSTOMER_PREFIX}".')

    return jira_client.issues_search(jql=f"project in ({','.join(project_keys)})", max_results=TOTAL_ISSUES_TO_RETRIEVE)


def __create_data_set(jira_client, jsm_client):
    service_desks = __get_all_service_desks_and_validate(jira_client, jsm_client)
    dataset = dict()
    dataset[AGENTS] = __get_agents(jira_client)
    dataset[CUSTOMERS] = __get_customers(jira_client, jsm_client, service_desks)
    issues = __get_issues_by_project_keys(jira_client, jsm_client,
                                          [project['projectKey'] for project in service_desks])
    dataset[REQUESTS] = __get_requests(jira_client, service_desks, issues)
    dataset[SERVICE_DESKS_LARGE], dataset[SERVICE_DESKS_MEDIUM], dataset[SERVICE_DESKS_SMALL] = __get_service_desks(
        jsm_client, jira_client, service_desks)
    dataset[REQUEST_TYPES] = __get_request_types(jsm_client, service_desks)
    dataset[CUSTOM_ISSUES] = __get_custom_issues(jira_client, jsm_client, JSM_SETTINGS.custom_dataset_query)
    dataset[INSIGHT_ISSUES] = list()
    dataset[INSIGHT_SCHEMAS] = list()
    if JSM_SETTINGS.insight:
        dataset[INSIGHT_ISSUES] = __get_insight_issues(jira_client)
        dataset[INSIGHT_SCHEMAS] = __get_insight_schemas(jsm_client)

    return dataset


@print_timing('Writing to file')
def __write_test_data_to_files(datasets):
    agents = [f"{user['name']},{DEFAULT_PASSWORD}" for user in datasets[AGENTS]]
    __write_to_file(JSM_DATASET_AGENTS, agents)
    __write_to_file(JSM_DATASET_CUSTOMERS, datasets[CUSTOMERS])
    __write_to_file(JSM_DATASET_REQUESTS, datasets[REQUESTS])
    __write_to_file(JSM_DATASET_SERVICE_DESKS_L, datasets[SERVICE_DESKS_LARGE])
    __write_to_file(JSM_DATASET_SERVICE_DESKS_S, datasets[SERVICE_DESKS_SMALL])
    __write_to_file(JSM_DATASET_SERVICE_DESKS_M, datasets[SERVICE_DESKS_MEDIUM])
    __write_to_file(JSM_DATASET_REQUEST_TYPES, datasets[REQUEST_TYPES])
    issues = [f"{issue['key']},{issue['id']},{issue['key'].split('-')[0]},{issue['service_desk_id']}" for issue
              in datasets[CUSTOM_ISSUES]]
    __write_to_file(JSM_DATASET_CUSTOM_ISSUES, issues)
    insight_issues = [f"{insight_issue['key']},{insight_issue['id']},{insight_issue['key'].split('-')[0]}"
                      for insight_issue
                      in datasets[INSIGHT_ISSUES]]
    __write_to_file(JSM_DATASET_INSIGHT_ISSUES, insight_issues)
    schemas_id = [f"{schema_id['id']}"
                  for schema_id
                  in datasets[INSIGHT_SCHEMAS]]
    __write_to_file(JSM_DATASET_INSIGHT_SCHEMAS, schemas_id)


@print_timing('JSM full prepare data', sep='=')
def main():
    print("Started preparing data")
    url = JSM_SETTINGS.server_url
    print("Server url: ", url)
    jsm_client = JsmRestClient(url, JSM_SETTINGS.admin_login, JSM_SETTINGS.admin_password, verify=JSM_SETTINGS.secure,
                               headers=JSM_EXPERIMENTAL_HEADERS)
    jira_client = JiraRestClient(url, JSM_SETTINGS.admin_login, JSM_SETTINGS.admin_password, JSM_SETTINGS.secure)
    dataset = __create_data_set(jira_client=jira_client, jsm_client=jsm_client)
    __write_test_data_to_files(dataset)


if __name__ == "__main__":
    main()
