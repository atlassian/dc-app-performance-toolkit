from selenium_ui.jsm import modules_agents
import pytest
from extension.jsm import extension_ui_agents  # noqa F401


def is_dataset_small(jsm_datasets):
    return len(jsm_datasets[modules_agents.SERVICE_DESKS_MEDIUM]) == 0


# this action should be the first one
def test_0_selenium_agent_a_login(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.login(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_browse_projects(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.agent_browse_projects(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_customers(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_customers(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_request(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_request(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_report_workload_medium(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if is_dataset_small(jsm_datasets):
        pytest.skip("Dataset does not have medium (10k-100k requests) service desk. Skipping action.")
    modules_agents.view_report_workload_medium(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_report_created_vs_resolved_medium(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if is_dataset_small(jsm_datasets):
        pytest.skip("Dataset does not have medium (10k-100k requests) service desk. Skipping action.")
    modules_agents.view_report_created_vs_resolved_medium(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_report_workload_small(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_report_workload_small(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_report_created_vs_resolved_small(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_report_created_vs_resolved_small(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_add_comment(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.add_comment(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_queues_medium(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    if is_dataset_small(jsm_datasets):
        pytest.skip("Dataset does not have medium (10k-100k requests) service desk. Skipping action.")
    modules_agents.view_queues_medium(jsm_webdriver, jsm_datasets)


def test_1_selenium_agent_view_queues_small(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.view_queues_small(jsm_webdriver, jsm_datasets)


"""
Add custom actions anywhere between login and log out action. Move this to a different line as needed.
Write your custom selenium scripts in `app/extension/jsm/extension_ui_agents.py`.
Refer to `app/selenium_ui/jsm/modules_agents.py` for examples.
"""
# def test_1_selenium_agent_custom_action(jsm_webdriver, jsm_datasets, jsm_screen_shots):
#     extension_ui_agents.app_specific_action(jsm_webdriver, jsm_datasets)


# this action should be the last one
def test_2_selenium_agent_z_logout(jsm_webdriver, jsm_datasets, jsm_screen_shots):
    modules_agents.logout(jsm_webdriver, jsm_datasets)
