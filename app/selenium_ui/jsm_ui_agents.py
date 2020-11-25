from selenium_ui.jsm import modules_agents
import pytest
from extension.jira import extension_ui  # TODO develop example of app-specific action for jsm


def is_dataset_small(jsm_datasets):
    return len(jsm_datasets[modules_agents.SERVICE_DESKS_MEDIUM]) == 0


# this action should be the first one
def test_0_agent_selenium_a_login(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.login(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_browse_service_desk_projects_list(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.browse_projects_list(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_browse_project_customers_page(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.browse_project_customers_page(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_customer_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_customer_request(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_workload_report_medium(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if is_dataset_small(jsm_datasets):
        pytest.skip("Dataset does not have medium (10k-100k requests) service desk. Skipping action.")
    modules_agents.view_workload_report_medium(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_time_to_resolution_report_medium(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if is_dataset_small(jsm_datasets):
        pytest.skip("Dataset does not have medium (10k-100k requests) service desk. Skipping action.")
    modules_agents.view_time_to_resolution_report_medium(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_created_vs_resolved_report_medium(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if is_dataset_small(jsm_datasets):
        pytest.mark.skipif("Dataset does not have medium (10k-100k requests) service desk. Skipping action.")
    modules_agents.view_created_vs_resolved_report_medium(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_workload_report_small(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_workload_report_small(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_time_to_resolution_report_small(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_time_to_resolution_report_small(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_created_vs_resolved_report_small(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_created_vs_resolved_report_small(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_add_request_comment(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.add_request_comment(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_queue_all_open_medium_project(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if is_dataset_small(jsm_datasets):
        pytest.skip("Dataset does not have medium (10k-100k requests) service desk. Skipping action.")
    modules_agents.view_queue_medium_project(jsm_webdriver, jsm_datasets)


def test_1_agent_selenium_view_queue_all_open_small_project(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_queue_small_project(jsm_webdriver, jsm_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jsm/extension_ui.py`.
Refer to `app/selenium_ui/jsm/modules_customers.py` for examples.
"""
# def test_1_selenium_custom_action(jira_webdriver, jira_datasets, jira_screen_shots):
#     extension_ui.app_specific_action(jira_webdriver, jira_datasets)


# this action should be the last one
def test_2_agent_selenium_z_log_out(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.log_out(jsm_webdriver, jsm_datasets)
