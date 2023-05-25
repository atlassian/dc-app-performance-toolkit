import pytest
import selenium_ui.conftest as conftest
from util.conf import JIRA_SETTINGS

@pytest.fixture(scope="module")
def jira_datasets():
    return conftest.application_dataset.jira_dataset()


@pytest.fixture(scope="module")
def jira_webdriver():
    return conftest.webdriver(app_settings=JIRA_SETTINGS)

@pytest.fixture
def jira_screen_shots(request, jira_webdriver):
    yield
    #conftest.get_screen_shots(request, jira_webdriver)
