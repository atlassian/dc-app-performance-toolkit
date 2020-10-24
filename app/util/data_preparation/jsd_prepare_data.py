from util.conf import JSD_SETTINGS
from util.project_paths import JSD_DATASET_AGENTS, JSD_DATASET_CUSTOMERS, JSD_DATASET_ISSUES, JSD_DATASET_SERVICE_DESKS
from util.api.jsd_clients import JsdRestClient
from util.api.jira_clients import JiraRestClient
from util.api.abstract_clients import JSD_EXPERIMENTAL_HEADERS
import math
import string
import random

ERROR_LIMIT = 10
DEFAULT_AGENT_PREFIX = 'performance_agent_'
DEFAULT_AGENT_APP_KEYS = ["jira-servicedesk"]
DEFAULT_CUSTOMER_PREFIX = 'performance_customer_'
DEFAULT_PASSWORD = 'password'

AGENTS = "agents"
CUSTOMERS = "customers"
ISSUES = "issues"
SERVICE_DESKS = "service_desks"
AGENT_PERCENTAGE = 25.00
# Issues to retrieve per project in percentage. E.g. retrieve 35% of issues from first project, 20% from second, etc.
# Retrieving 5% of all issues from projects 10-last project.
PROJECTS_ISSUES_PERC = {1: 35, 2: 20, 3: 15, 4: 5, 5: 5, 6: 5, 7: 2, 8: 2, 9: 2, 10: 2}

TOTAL_ISSUES_TO_RETRIEVE = 100

performance_agents_count = math.ceil(JSD_SETTINGS.concurrency * AGENT_PERCENTAGE / 100)
performance_customers_count = JSD_SETTINGS.concurrency - performance_agents_count


def __calculate_issues_per_project(projects_count):
    calculated_issues_per_project_count = {}
    max_percentage_key = max(PROJECTS_ISSUES_PERC, key=int)
    if projects_count > max_percentage_key:
        percent_for_other_projects = math.ceil((100 - sum(PROJECTS_ISSUES_PERC.values())) /
                                               (projects_count - max(PROJECTS_ISSUES_PERC, key=int)))
    else:
        percent_for_other_projects = 0

    for key, value in PROJECTS_ISSUES_PERC.items():
        calculated_issues_per_project_count[key] = math.ceil(value * TOTAL_ISSUES_TO_RETRIEVE / 100)
    for project_index in range(1, projects_count + 1):
        if project_index not in calculated_issues_per_project_count.keys():
            calculated_issues_per_project_count[project_index] = math.ceil(percent_for_other_projects *
                                                                           TOTAL_ISSUES_TO_RETRIEVE / 100)

    return calculated_issues_per_project_count


def __get_customers_with_requests(jira_client, jsd_client, count):
    customers_with_requests = []
    customers_without_requests = []
    start_at = 0
    while len(customers_with_requests) < count:
        customers = jira_client.get_users(username=DEFAULT_CUSTOMER_PREFIX, max_results=count, start_at=start_at)
        if not customers:
            break
        start_at = start_at + count

        for customer in customers:
            customer_auth = (customer['name'], DEFAULT_PASSWORD)
            customer_requests = jsd_client.get_request(auth=customer_auth)['values']
            if customer_requests:
                customer_dict = {'name': customer['name']}
                requests = []
                for request in customer_requests:
                    requests.append((request['serviceDeskId'], request['issueKey']))
                customer_dict['requests'] = requests
                customers_with_requests.append(customer_dict)
            else:
                customers_without_requests.append(customer)
    print(f'Retrieved customers with requests: {len(customers_with_requests)}, '
          f'customers without requests: {len(customers_without_requests)}')

    if len(customers_with_requests) < count:
        customers_to_add = count - len(customers_with_requests)
        if len(customers_without_requests) >= customers_to_add:
            customers_with_requests.extend(customers_without_requests[:customers_to_add])
        else:
            customers_with_requests.extend(customers_without_requests)

    return customers_with_requests


def __get_jsd_users(jira_client, jsd_client=None, is_agent=False):
    if is_agent:
        prefix_name, application_keys, count = DEFAULT_AGENT_PREFIX, DEFAULT_AGENT_APP_KEYS, performance_agents_count
        perf_users = jira_client.get_users(username=prefix_name, max_results=count)
    else:
        prefix_name, application_keys, count = DEFAULT_CUSTOMER_PREFIX, None, performance_customers_count
        perf_users = __get_customers_with_requests(jsd_client=jsd_client, jira_client=jira_client, count=count)
    retrieved_per_users_count = len(perf_users)
    users_to_create = count - len(perf_users)
    if users_to_create > 0:
        add_users = generate_users(api=jira_client, num_to_create=users_to_create, prefix_name=prefix_name,
                                   application_keys=application_keys)
        if not add_users:
            raise SystemExit(f"Jira Service Desk could not create users with prefix: {prefix_name}. "
                             f"There were {len(perf_users)}/{count} retrieved.")
        perf_users.extend(add_users)
    print(f'Retrieved {retrieved_per_users_count} with prefix {prefix_name}, generated {users_to_create}')
    print('---------------------------------------------------')
    return perf_users


def __get_agents(api):
    return __get_jsd_users(api, is_agent=True)


def __get_customers(jira_client, jsd_client):
    customers = __get_jsd_users(jira_client, jsd_client=jsd_client, is_agent=False)

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
            print(f"Warning: Create Jira user error: {error}. Retry limits {errors_count}/{ERROR_LIMIT}")
            errors_count = errors_count + 1
    return created_agents


def __get_service_desks(jsd_api):
    service_desks = jsd_api.get_all_service_desks()
    if not service_desks:
        raise Exception('ERROR: There are no Jira Service Desks were found')
    service_desks_list = [','.join((service_desk["id"],
                                    service_desk["projectId"],
                                    service_desk["projectKey"])) for service_desk in service_desks]
    print(f"Retrieved {len(service_desks)} Jira Service Desks")
    return service_desks_list


def __get_requests(jsd_api, jira_api):
    service_desks_issues = []
    service_desks = jsd_api.get_all_service_desks()
    for service_desk in service_desks:
        service_desk_dict = dict()
        service_desk_dict['serviceDeskId'] = service_desk['id']
        service_desk_dict['projectId'] = service_desk['projectId']
        service_desk_dict['projectKey'] = service_desk['projectKey']
        service_desks_issues.append(service_desk_dict)

    issues_disctribution_perc = __calculate_issues_per_project(len(service_desks))
    issues_disctribution_id = {}
    for key, value in issues_disctribution_perc.items():
        issues_disctribution_id[service_desks_issues[key-1]['projectKey']] = value

    print(f'Start retrieving issues by distribution per project: {issues_disctribution_id}')
    distribution_success = True
    issues_list = []
    for service_desk in service_desks_issues:
        issues = jira_api.issues_search(jql=f'project = {service_desk["projectKey"]}',
                                        max_results=issues_disctribution_id[service_desk['projectKey']])

        issues_per_project_list = [','.join((issue['id'],
                                             issue['key'],
                                             service_desk['serviceDeskId'],
                                             service_desk['projectId'],
                                             service_desk['projectKey'])) for issue in issues]

        issues_list.extend(issues_per_project_list)
        if len(issues) < issues_disctribution_id[service_desk['projectKey']]:
            print(f'Stop retrieving issues by distribution. Project {service_desk["projectKey"]} '
                  f'has {len(issues)}/{issues_disctribution_id[service_desk["projectKey"]]} issues')
            distribution_success = False
            break

    if distribution_success:
        print(f'Issues retrieving by distribution per project finished successfully. '
              f'Retrieved {len(issues_list)} issues')
        print('---------------------------------------------------')
        return issues_list

    print(f'Force retrieving {TOTAL_ISSUES_TO_RETRIEVE} issues from Service Desk projects')
    projects_keys = ','.join([project['projectKey'] for project in service_desks])
    issues = jira_api.issues_search(jql=f"project in ({projects_keys})", max_results=TOTAL_ISSUES_TO_RETRIEVE)
    if len(issues) < TOTAL_ISSUES_TO_RETRIEVE:
        raise Exception(f"ERROR: Jira Service Desks does not have enough issues "
                        f"{len(issues)}/{TOTAL_ISSUES_TO_RETRIEVE}")
    issues_list = []
    for issue in issues:
        for service_desk in service_desks_issues:
            if service_desk['projectKey'] in issue['key']:
                issue_str = f'{issue["id"]},' \
                            f'{issue["key"]},' \
                            f'{service_desk["serviceDeskId"]},' \
                            f'{service_desk["projectId"]},' \
                            f'{service_desk["projectKey"]}'

                issues_list.append(issue_str)
    print(f"Force retrieved {len(issues_list)} issues.")
    print('---------------------------------------------------')
    return issues_list


def generate_random_string(length = 20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __write_to_file(file_path, items):
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")


def __create_data_set(jira_client, jsd_client):
    dataset = dict()
    dataset[AGENTS] = __get_agents(jira_client)
    dataset[CUSTOMERS] = __get_customers(jira_client, jsd_client)
    dataset[ISSUES] = __get_requests(jira_api=jira_client, jsd_api=jsd_client)
    dataset[SERVICE_DESKS] = __get_service_desks(jsd_api=jsd_client)

    return dataset


def write_test_data_to_files(datasets):
    agents = [f"{user['name']},{DEFAULT_PASSWORD}" for user in datasets[AGENTS]]
    __write_to_file(JSD_DATASET_AGENTS, agents)

    __write_to_file(JSD_DATASET_CUSTOMERS, datasets[CUSTOMERS])
    __write_to_file(JSD_DATASET_ISSUES, datasets[ISSUES])
    __write_to_file(JSD_DATASET_SERVICE_DESKS, datasets[SERVICE_DESKS])


def main():
    print("Started preparing data")
    url = JSD_SETTINGS.server_url
    print("Server url: ", url)

    jsd_client = JsdRestClient(url, JSD_SETTINGS.admin_login, JSD_SETTINGS.admin_password,
                               headers=JSD_EXPERIMENTAL_HEADERS)
    jira_client = JiraRestClient(url, JSD_SETTINGS.admin_login, JSD_SETTINGS.admin_password)

    import time
    time_now = time.time()
    dataset = __create_data_set(jira_client=jira_client, jsd_client=jsd_client)
    write_test_data_to_files(dataset)
    print("--- %s seconds ---" % (time.time() - time_now))  # TODO delete it after fully developing prepare_data.py


if __name__ == "__main__":
    main()

