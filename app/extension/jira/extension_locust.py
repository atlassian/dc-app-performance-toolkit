import json
import random
import re
from locustio.jira.requests_params import jira_datasets
from locustio.common_utils import init_logger, jira_measure, RESOURCE_HEADERS, ADMIN_HEADERS, generate_random_string

logger = init_logger(app_type='jira')
jira_dataset = jira_datasets()



@jira_measure("locust_app_specific_action")
# @run_as_specific_user(username='admin', password='admin')  # run as specific user
def app_specific_action(locust):
    # Select Projecy 
    project = random.choice(jira_dataset['projects'])
    project_id = project[1]

    # Get issue type for the project
    response = locust.get(f'/rest/api/2/issue/createmeta?projectIds={project_id}', headers=RESOURCE_HEADERS)
    content = json.loads(response.content)
    project_key = content["projects"][0]["key"] 
    issue_type = content["projects"][0]["issuetypes"][0]["name"]
    logger.locust_info(f"Project Key: {project_key}")
    logger.locust_info(f"issue_type: {issue_type}")
    
    # Create issue in project
    summary = f'Locust summary {generate_random_string(10, only_letters=True)}'
    description = f'Locust description {generate_random_string(10)}'
    incident_id = f'IncidentId:{generate_random_string(5)}'

    body = {"fields": {"project": {"key": project_key}, "summary": f"{summary}", "description": f"{description}", "priority": { "name": "High" }, "labels":[f"{incident_id}"], "issuetype": {"name": issue_type}}}
    logger.locust_info(f"Json Body: {body}")
    response = locust.post(f'/rest/api/2/issue', headers=ADMIN_HEADERS, json=body)

