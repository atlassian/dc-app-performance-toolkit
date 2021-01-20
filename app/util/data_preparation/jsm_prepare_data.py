import functools
import multiprocessing
import random
import string
from datetime import timedelta
from timeit import default_timer as timer
import datetime
import urllib3

from util.api.abstract_clients import JSM_EXPERIMENTAL_HEADERS
from util.api.jira_clients import JiraRestClient
from util.api.jsm_clients import JsmRestClient
from util.conf import JSM_SETTINGS
from util.project_paths import JSM_DATASET_AGENTS, JSM_DATASET_CUSTOMERS, JSM_DATASET_REQUESTS, \
    JSM_DATASET_SERVICE_DESKS_L, JSM_DATASET_SERVICE_DESKS_M, JSM_DATASET_SERVICE_DESKS_S, JSM_DATASET_REQUEST_TYPES, \
    JSM_DATASET_CUSTOM_ISSUES

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
num_cores = multiprocessing.cpu_count()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def print_timing(message):
    assert message is not None, "Message is not passed to print_timing decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = timer()
            result = func(*args, **kwargs)
            end = timer()
            print(f"{message} finished in {timedelta(seconds=end-start)} seconds")
            print('------------------------------------------------------')
            return result
        return wrapper
    return deco_wrapper


def __calculate_issues_per_project(projects_count):
    calculated_issues_per_project_count = {}
    max_percentage_key = max(PROJECTS_ISSUES_PERC, key=int)
    if projects_count > max_percentage_key:
        percent_for_other_projects = round((100 - sum(PROJECTS_ISSUES_PERC.values())) /
                                           (projects_count - max(PROJECTS_ISSUES_PERC, key=int)), 3)
        calculated_issues_percentage = PROJECTS_ISSUES_PERC
    else:
        percent_for_other_projects = 0
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
    customer_requests = jsm_client.get_request(auth=customer_auth)
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
        pool = multiprocessing.pool.ThreadPool(processes=num_cores)  # Can be increased to improve script speed

        for customer_chunk in customer_chunks:
            if len(customers_with_requests) >= count:
                break
            customers_datas = pool.starmap(__filter_customer_with_requests, [(i, jsm_client) for i in customer_chunk])
            for customer_data in customers_datas:
                if customer_data['has_requests']:
                    if len(customers_with_requests) >= count:
                        break
                    customers_with_requests.append(customer_data)
                else:
                    customers_without_requests.append(customer_data)

    print(f'Retrieved customers with requests: {len(customers_with_requests)}')

    return customers_with_requests


def __get_jsm_users(jira_client, jsm_client=None, is_agent=False):
    if is_agent:
        prefix_name, application_keys, count = DEFAULT_AGENT_PREFIX, DEFAULT_AGENT_APP_KEYS, performance_agents_count
        perf_users = jira_client.get_users(username=prefix_name, max_results=count)
        users_to_create = count - len(perf_users)
        if users_to_create > 0:
            add_users = generate_users(api=jira_client, num_to_create=users_to_create, prefix_name=prefix_name,
                                       application_keys=application_keys)
            if not add_users:
                raise Exception(f"ERROR: Jira Service Management could not create agent"
                                f"There were {len(perf_users)}/{count} retrieved.")
            perf_users.extend(add_users)
        return perf_users
    else:
        prefix_name, application_keys, count = DEFAULT_CUSTOMER_PREFIX, None, performance_customers_count
        perf_users = jira_client.get_users(username=prefix_name, max_results=count)
        users_to_create = count - len(perf_users)
        if users_to_create > 0:
            add_users = generate_users(api=jira_client, num_to_create=users_to_create, prefix_name=prefix_name,
                                       application_keys=[])
            if not add_users:
                raise Exception(f"ERROR: Jira Service Management could not create customers"
                                f"There were {len(perf_users)}/{count} retrieved.")
        perf_users_with_requests = __get_customers_with_requests(
            jsm_client=jsm_client, jira_client=jira_client, count=count)
        if len(perf_users_with_requests) < performance_customers_count:
            raise Exception(f'ERROR: Not enough customers with prefix "{DEFAULT_CUSTOMER_PREFIX}" '
                            f'with requests were found: '
                            f'{len(perf_users_with_requests)}/{performance_customers_count}. '
                            f'Please review the "concurrency_customers" value in jsm.yml file and/or '
                            f'create requests on behalf of customers with prefix "{DEFAULT_CUSTOMER_PREFIX}".')
        return perf_users_with_requests


@print_timing('Retrieved agents')
def __get_agents(jira_client):
    now = datetime.datetime.now()
    print(f'Agents start {now.strftime("%H:%M:%S")}')
    return __get_jsm_users(jira_client, is_agent=True)


@print_timing('Retrieved customers')
def __get_customers(jira_client, jsm_client):
    now = datetime.datetime.now()
    print(f'Customers start {now.strftime("%H:%M:%S")}')
    customers = __get_jsm_users(jira_client, jsm_client=jsm_client, is_agent=False)
    customers_list = []
    for customer in customers:
        default_customer = f'{customer["name"]},{DEFAULT_PASSWORD}'
        if 'requests' in customer.keys():
            default_customer = f"{default_customer},{','.join([','.join(i) for i in customer['requests']])}"
            customers_list.append(default_customer)
        else:
            customers_list.append(default_customer)
    return customers_list


def generate_users(api, num_to_create, application_keys, prefix_name):
    errors_count = 0
    created_agents = []
    while len(created_agents) < num_to_create:
        if errors_count >= ERROR_LIMIT:
            raise Exception(f'ERROR: Maximum error limit reached {errors_count}/{ERROR_LIMIT}. '
                            f'Please check the errors in bzt.log')
        username = f"{prefix_name}{generate_random_string(10)}"
        try:
            agent = api.create_user(name=username, password=DEFAULT_PASSWORD,
                                    application_keys=application_keys)
            created_agents.append(agent)
        except Exception as error:
            print(f"WARNING: Create Jira user error: {error}. Retry limits {errors_count}/{ERROR_LIMIT}")
            errors_count = errors_count + 1
    return created_agents


def __get_service_desk_info(jira_api, jsm_api, service_desk):
    # Run in parallel 'get_total_issues_count', 'get_queue' and '__get_service_desk_reports'.
    pool = multiprocessing.pool.ThreadPool(processes=3)
    p1 = pool.apply_async(jira_api.get_total_issues_count, kwds={'jql': f'project = {service_desk["projectKey"]}'})
    p2 = pool.apply_async(jsm_api.get_queue, kwds={'service_desk_id': service_desk['id']})
    p3 = pool.apply_async(__get_service_desk_reports, kwds={'service_desk': service_desk, 'jsm_api': jsm_api})

    service_desk_requests_count = str(p1.get())
    service_desk_queues = p2.get()
    service_desk_reports = p3.get()

    all_open_queue_id = [queue['id'] for queue in service_desk_queues if queue['name'] == 'All open']
    if not all_open_queue_id:
        raise Exception(f'ERROR: Service Desk with id {service_desk} does not have "All open" queue')
    all_open_queue_id = ''.join(all_open_queue_id)
    service_desk['total_requests'] = service_desk_requests_count
    service_desk['all_open_queue_id'] = all_open_queue_id
    service_desk['created_vs_resolved_id'] = service_desk_reports['created_vs_resolved_id']
    service_desk['time_to_resolution_id'] = service_desk_reports['time_to_resolution_id']
    return service_desk


@print_timing('Retrieved service desks')
def __get_service_desks(jsm_api, jira_api, service_desks):
    now = datetime.datetime.now()
    print(f'Service desks start {now.strftime("%H:%M:%S")}')
    pool = multiprocessing.pool.ThreadPool(processes=num_cores*2)
    service_desks_with_requests = pool.starmap(__get_service_desk_info, [(jira_api, jsm_api, service_desk)
                                               for service_desk in service_desks])

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
    issues = jira_api.issues_search_parallel(jql=f'project = {service_desk["projectKey"]}',
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


@print_timing('Retrieved customers requests')
def __get_requests(jira_api, service_desks, requests_without_distribution):
    now = datetime.datetime.now()
    print(f'Requests start {now.strftime("%H:%M:%S")}')
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
        issues_distribution_id[service_desks_issues[key-1]['projectKey']] = value

    print(f'Start retrieving issues by distribution per project: {issues_distribution_id}')
    distribution_success = True
    pool = multiprocessing.pool.ThreadPool(processes=num_cores)
    issues_list = pool.starmap(__get_service_desk_requests, [(jira_api, issues_distribution_id, i)
                                                             for i in service_desks_issues])
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


def generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __write_to_file(file_path, items):
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")


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


def __get_request_types(jsm_api, service_desks):
    pool = multiprocessing.pool.ThreadPool(processes=num_cores * 2)
    requests_ids = pool.starmap(__get_service_desk_request_types,
                                [(jsm_api, service_desk) for service_desk in service_desks])
    requests_ids = sum(requests_ids, [])
    request_types_list = []
    for request_id in requests_ids:
        if request_id['request_type_name'] in REQUEST_TYPES_NAMES:
            request_types_list.append([request_id['project_id'],
                                       request_id['service_desk_id'],
                                       request_id['request_type_id']])
    return [','.join(i) for i in request_types_list]


def __get_custom_issues(jira_api, jsm_api, custom_jql):
    issues = []
    if custom_jql:
        issues = jira_api.issues_search(
            jql=custom_jql, max_results=8000
        )
    for issue in issues:
        expanded_issue = jsm_api.get_request(issue_id_or_key=issue['key'])
        issue['service_desk_id'] = expanded_issue[0]['serviceDeskId']
    if not issues:
        print(f"There are no issues found using JQL {custom_jql}")
    return issues


def __create_data_set(jira_client, jsm_client):
    dataset = dict()
    service_desks = jsm_client.get_all_service_desks()
    if not service_desks:
        raise Exception('ERROR: There were no Jira Service Desks found')
    if len(service_desks) < 2:
        raise Exception('ERROR: At least 2 service desks are needed')
    # TODO improve organizations check to actually verify if service desk projects have orgs with performance_customers
    organizations = jsm_client.get_all_organizations()
    perf_organizations = [org for org in organizations if DEFAULT_ORGANIZATION in org['name']]
    if not perf_organizations:
        raise Exception(f'ERROR: There were no organizations found with prefix "{DEFAULT_ORGANIZATION}". '
                        f'Make sure JSM projects has organizations with prefix "{DEFAULT_ORGANIZATION}". '
                        f'Organizations "{DEFAULT_ORGANIZATION}" should have customers'
                        f' with prefix "{DEFAULT_CUSTOMER_PREFIX}".')
    projects_keys = ','.join([project['projectKey'] for project in service_desks])
    requests = jira_client.issues_search_parallel(jql=f"project in ({projects_keys})",
                                                  max_results=TOTAL_ISSUES_TO_RETRIEVE)

    pool = multiprocessing.pool.ThreadPool(processes=num_cores)
    agents_pool = pool.apply_async(__get_agents, kwds={'jira_client': jira_client})
    customers_pool = pool.apply_async(__get_customers, kwds={'jira_client': jira_client, 'jsm_client': jsm_client})
    requests_pool = pool.apply_async(__get_requests, kwds={'jira_api': jira_client,
                                                           'service_desks': service_desks,
                                                           'requests_without_distribution': requests})
    service_desks_pool = pool.apply_async(__get_service_desks, kwds={'jsm_api': jsm_client,
                                                                     'jira_api': jira_client,
                                                                     'service_desks': service_desks})

    dataset[AGENTS] = agents_pool.get()
    dataset[CUSTOMERS] = customers_pool.get()
    dataset[REQUESTS] = requests_pool.get()
    dataset[SERVICE_DESKS_LARGE], dataset[SERVICE_DESKS_MEDIUM], dataset[SERVICE_DESKS_SMALL] = service_desks_pool.get()
    requests_types = pool.apply_async(__get_request_types, kwds={'jsm_api': jsm_client,
                                                                 'service_desks': service_desks})
    dataset[REQUEST_TYPES] = requests_types.get()
    dataset[CUSTOM_ISSUES] = __get_custom_issues(jira_client, jsm_client, JSM_SETTINGS.custom_dataset_query)

    return dataset


def write_test_data_to_files(datasets):
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


@print_timing('Full prepare data')
def main():
    print("Started preparing data")
    url = JSM_SETTINGS.server_url
    print("Server url: ", url)
    jsm_client = JsmRestClient(url, JSM_SETTINGS.admin_login, JSM_SETTINGS.admin_password, verify=JSM_SETTINGS.secure,
                               headers=JSM_EXPERIMENTAL_HEADERS)
    jira_client = JiraRestClient(url, JSM_SETTINGS.admin_login, JSM_SETTINGS.admin_password, JSM_SETTINGS.secure)
    dataset = __create_data_set(jira_client=jira_client, jsm_client=jsm_client)
    write_test_data_to_files(dataset)


if __name__ == "__main__":
    main()
