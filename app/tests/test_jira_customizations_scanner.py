import inspect
from types import SimpleNamespace
import sys
from pathlib import Path

import pytest
import yaml
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from extension.jira import extension_ui
from selenium_ui.jira.pages.pages import AdminPage
from selenium_ui.jira.pages.selectors import AdminLocators, LoginPageLocators
from util.conf import CustomizationInsightsSettings


APP_DIRECTORY = Path(__file__).resolve().parents[1]
JIRA_CONFIG_PATH = APP_DIRECTORY / "jira.yml"
SCANNER_OVERLAY_PATH = APP_DIRECTORY / "jira-customizations-scanner.yml"


def load_yaml(path):
    with path.open() as config_file:
        return yaml.safe_load(config_file)


def test_jira_base_profile_has_standard_run_four_and_scanner_contract():
    config = load_yaml(JIRA_CONFIG_PATH)
    env = config["settings"]["env"]
    properties = config["scenarios"]["jmeter"]["properties"]

    assert env["concurrency"] == 200
    assert env["test_duration"] == "45m"
    assert env["ramp-up"] == "3m"
    assert env["customization_insights_enabled"] is True
    assert env["customization_insights_status_selector_type"] == "id"
    assert env["customization_insights_status_selector"] == "scan-panel-summary"
    assert env["customization_insights_in_progress_text"] == "In progress"
    assert env["customization_insights_completed_text"] == "Done"
    assert env["customization_insights_scan_timeout"] == 1200
    assert env["standalone_extension"] == 0
    assert "customization_insights_rest_path" not in env
    assert "customization_insights_rest_assertion" not in env
    assert "customization_insights_rest_path" not in properties
    assert "customization_insights_rest_assertion" not in properties
    assert config["execution"] == [
        {
            "scenario": "${load_executor}",
            "executor": "${load_executor}",
            "concurrency": "${concurrency}",
            "hold-for": "${test_duration}",
            "ramp-up": "${ramp-up}",
        },
        {
            "scenario": "selenium",
            "executor": "selenium",
            "runner": "pytest",
            "iterations": 1,
            "hold-for": "${test_duration}",
        },
    ]


def test_scanner_overlay_replaces_executions_with_short_delayed_selenium_run():
    assert SCANNER_OVERLAY_PATH.exists()

    config = load_yaml(SCANNER_OVERLAY_PATH)
    executions = config["~execution"]

    assert config["settings"]["env"]["test_duration"] == "25m"
    assert len(executions) == 2
    assert executions[0] == {
        "scenario": "${load_executor}",
        "executor": "${load_executor}",
        "concurrency": "${concurrency}",
        "hold-for": "${test_duration}",
        "ramp-up": "${ramp-up}",
    }
    assert executions[1] == {
        "scenario": "selenium",
        "executor": "selenium",
        "runner": "pytest",
        "hold-for": "${test_duration}",
        "delay": "${ramp-up}",
        "iterations": 1,
    }


class FakeElement:
    def is_displayed(self):
        return True


def scanner_config(**overrides):
    settings = {
        "new_scan_selector": "new-scan-btn",
        "status_selector_type": "id",
        "status_selector": "scan-panel-summary",
        "in_progress_text": "In progress",
        "completed_text": "Done",
        "scan_timeout": 42,
    }
    settings.update(overrides)
    return SimpleNamespace(**settings)


class StatusElement:
    def __init__(self, text):
        self.text = text


class StatusDriver:
    def __init__(self, status_texts):
        self._status_texts = iter(status_texts)
        self.find_calls = []

    def find_element(self, by, value):
        self.find_calls.append((by, value))
        return StatusElement(next(self._status_texts))


class PollingWait:
    timeouts = []

    def __init__(self, webdriver, timeout):
        self.webdriver = webdriver
        self.timeout = timeout
        self.timeouts.append(timeout)

    def until(self, predicate):
        for _ in range(10):
            if predicate(self.webdriver):
                return
        raise TimeoutException("status text was not observed")


@pytest.mark.parametrize(
    "env_settings",
    [
        {
            "customization_insights_status_selector_type": "id",
            "customization_insights_status_selector": "scan-panel-summary",
            "customization_insights_in_progress_text": "In progress",
        },
        {
            "customization_insights": {
                "status_selector_type": "id",
                "status_selector": "scan-panel-summary",
                "in_progress_text": "In progress",
            },
        },
    ],
)
def test_customization_insights_settings_read_status_contract_from_both_yaml_shapes(env_settings):
    settings = CustomizationInsightsSettings(env_settings)

    assert settings.status_selector_type == "id"
    assert settings.status_selector == "scan-panel-summary"
    assert settings.in_progress_text == "In progress"


def test_flat_scanner_disable_overrides_nested_enable():
    settings = CustomizationInsightsSettings({
        "customization_insights_enabled": False,
        "customization_insights": {"enabled": True},
    })

    assert settings.enabled is False


def test_scanner_status_uses_configured_selector_type_and_value():
    driver = StatusDriver(["In progress"])

    status = extension_ui._scanner_status(driver, scanner_config())

    assert status == "In progress"
    assert driver.find_calls == [(extension_ui.By.ID, "scan-panel-summary")]


def test_full_scan_waits_for_configured_in_progress_then_completed_status(monkeypatch):
    class Button:
        def __init__(self):
            self.clicked = False

        def click(self):
            self.clicked = True

    class ScanDriver(StatusDriver):
        def __init__(self):
            super().__init__(["Queued", "In progress", "In progress", "Done"])
            self.button = Button()

        def find_element(self, by, value):
            if value == "new-scan-btn":
                return self.button
            return super().find_element(by, value)

        def execute_script(self, *args):
            pass

    PollingWait.timeouts = []
    monkeypatch.setattr(extension_ui, "WebDriverWait", PollingWait)
    monkeypatch.setattr(extension_ui, "_dismiss_aui_messages", lambda webdriver: None)
    driver = ScanDriver()

    extension_ui._run_full_scan.__wrapped__(driver, scanner_config())

    assert driver.button.clicked
    assert PollingWait.timeouts == [60, 42]
    assert driver.find_calls == [
        (extension_ui.By.ID, "scan-panel-summary"),
        (extension_ui.By.ID, "scan-panel-summary"),
        (extension_ui.By.ID, "scan-panel-summary"),
        (extension_ui.By.ID, "scan-panel-summary"),
    ]


def test_full_scan_raises_actionable_error_when_new_scan_click_fails(monkeypatch):
    class FailingButton:
        def click(self):
            raise WebDriverException("button is unavailable")

    class ScanDriver:
        def find_element(self, by, value):
            return FailingButton()

        def execute_script(self, *args):
            pass

    monkeypatch.setattr(extension_ui, "_dismiss_aui_messages", lambda webdriver: None)

    with pytest.raises(RuntimeError, match="Unable to start Customizations Scanner scan"):
        extension_ui._run_full_scan.__wrapped__(ScanDriver(), scanner_config())


def test_scan_start_timeout_remains_an_actionable_failure(monkeypatch):
    class TimeoutWait:
        def __init__(self, webdriver, timeout):
            pass

        def until(self, predicate):
            raise TimeoutException("status text was not observed")

    monkeypatch.setattr(extension_ui, "WebDriverWait", TimeoutWait)

    with pytest.raises(RuntimeError, match="did not start"):
        extension_ui._wait_until_started(StatusDriver(["Queued"]), scanner_config())


def test_scan_completion_timeout_remains_an_actionable_failure(monkeypatch):
    class TimeoutWait:
        def __init__(self, webdriver, timeout):
            pass

        def until(self, predicate):
            raise TimeoutException("status text was not observed")

    monkeypatch.setattr(extension_ui, "WebDriverWait", TimeoutWait)

    with pytest.raises(RuntimeError, match="did not complete"):
        extension_ui._wait_until_completed(StatusDriver(["In progress"]), scanner_config())


def test_full_scan_timer_wraps_only_click_and_status_waits(monkeypatch):
    calls = []
    monkeypatch.setattr(extension_ui, "_click_new_scan", lambda driver, config: calls.append("click"))
    monkeypatch.setattr(extension_ui, "_wait_until_started", lambda driver, config: calls.append("started"))
    monkeypatch.setattr(extension_ui, "_wait_until_completed", lambda driver, config: calls.append("completed"))

    extension_ui._run_full_scan.__wrapped__(object(), scanner_config())

    timing_closure = inspect.getclosurevars(extension_ui._run_full_scan)
    assert timing_closure.nonlocals["interaction"] == "selenium_customizations_scanner:full_scan"
    assert calls == ["click", "started", "completed"]


class LoginGatewayDriver:
    current_url = (
        "http://jira.example/jira/login.jsp?permissionViolation=true"
        "&os_destination=%2Fsecure%2Fadmin%2FViewApplicationProperties.jspa"
    )

    def get(self, url):
        self.requested_url = url

    def find_elements(self, by, value):
        present = {
            AdminLocators.login_form,
            LoginPageLocators.login_field_2sv,
            LoginPageLocators.password_field_2sv,
        }
        return [FakeElement()] if (by, value) in present else []

    def find_element(self, by, value):
        elements = self.find_elements(by, value)
        if not elements:
            raise NoSuchElementException(f"No fake element for {(by, value)}")
        return elements[0]


def test_jira_admin_page_rejects_plain_login_gateway():
    admin_page = AdminPage(LoginGatewayDriver())

    with pytest.raises(RuntimeError, match="authenticated Jira admin session"):
        admin_page.go_to(password="admin")


def test_customizations_scanner_login_redirect_fails_before_waiting_for_button(monkeypatch):
    class FakeLogin:
        def __init__(self, webdriver):
            pass

        def delete_all_cookies(self):
            pass

        def go_to(self):
            pass

        def wait_for_login_page_loaded(self):
            pass

        def set_credentials(self, username, password):
            pass

        def wait_for_dashboard_or_first_login_loaded(self):
            pass

        def is_first_login(self):
            return False

        def is_first_login_second_page(self):
            return False

        def wait_for_page_loaded(self):
            pass

    class FakeAdminPage:
        def __init__(self, webdriver):
            pass

        def go_to(self, password=None):
            pass

    class FakePage:
        def __init__(self, webdriver):
            self.webdriver = webdriver

        def go_to_url(self, url):
            self.webdriver.current_url = (
                "http://jira.example/jira/login.jsp?permissionViolation=true"
                "&os_destination=%2Fplugins%2Fservlet%2Fcustomizations-scanner"
            )
            self.webdriver.page_source = (
                '<meta name="ajs-remote-user" content="">'
                '<form id="login-form"><p>You must log in to access this page.</p></form>'
            )

        def wait_until_visible(self, selector):
            raise AssertionError("scanner button wait should not run after login redirect")

    monkeypatch.setattr(extension_ui, "Login", FakeLogin)
    monkeypatch.setattr(extension_ui, "AdminPage", FakeAdminPage)
    monkeypatch.setattr(extension_ui, "BasePage", FakePage)
    monkeypatch.setattr(extension_ui, "print_timing", lambda *args, **kwargs: lambda func: func)
    monkeypatch.setattr(
        extension_ui.JIRA_SETTINGS,
        "customization_insights",
        SimpleNamespace(
            enabled=True,
            ui_path="/plugins/servlet/customizations-scanner",
            ready_selector="new-scan-btn",
            ready_selector_type="id",
            new_scan_selector="new-scan-btn",
            completed_text="Done",
            scan_timeout=1200,
        ),
    )

    driver = SimpleNamespace(current_url="", page_source="")

    with pytest.raises(RuntimeError, match="redirected to Jira login"):
        extension_ui.app_specific_action(driver, {})


def test_customizations_scanner_reauthenticates_once_after_login_redirect(monkeypatch):
    login_calls = []
    websudo_calls = []
    scanner_visits = []
    scanner_waits = []

    class FakeLogin:
        def __init__(self, webdriver):
            pass

        def delete_all_cookies(self):
            pass

        def go_to(self):
            pass

        def wait_for_login_page_loaded(self):
            pass

        def set_credentials(self, username, password):
            login_calls.append((username, password))

        def wait_for_dashboard_or_first_login_loaded(self):
            pass

        def is_first_login(self):
            return False

        def is_first_login_second_page(self):
            return False

        def wait_for_page_loaded(self):
            pass

    class FakeAdminPage:
        def __init__(self, webdriver):
            pass

        def go_to(self, password=None):
            websudo_calls.append(password)

    class FakePage:
        def __init__(self, webdriver):
            self.webdriver = webdriver

        def go_to_url(self, url):
            scanner_visits.append(url)
            if len(scanner_visits) == 1:
                self.webdriver.current_url = (
                    "http://jira.example/jira/login.jsp?permissionViolation=true"
                    "&os_destination=%2Fplugins%2Fservlet%2Fcustomizations-scanner"
                )
                self.webdriver.page_source = (
                    '<form id="login-form"><p>You must log in to access this page.</p></form>'
                )
            else:
                self.webdriver.current_url = "http://jira.example/jira/plugins/servlet/customizations-scanner"
                self.webdriver.page_source = '<button id="new-scan-btn">New scan</button>'

        def wait_until_visible(self, selector):
            scanner_waits.append(selector)
            return FakeElement()

        def wait_for_dom_mutations_complete(self):
            pass

    monkeypatch.setattr(extension_ui, "Login", FakeLogin)
    monkeypatch.setattr(extension_ui, "AdminPage", FakeAdminPage)
    monkeypatch.setattr(extension_ui, "BasePage", FakePage)
    monkeypatch.setattr(extension_ui, "print_timing", lambda *args, **kwargs: lambda func: func)
    monkeypatch.setattr(extension_ui, "_dismiss_aui_messages", lambda webdriver: None)
    monkeypatch.setattr(extension_ui, "_run_full_scan", lambda webdriver, config: None)
    monkeypatch.setattr(
        extension_ui.JIRA_SETTINGS,
        "customization_insights",
        SimpleNamespace(
            enabled=True,
            ui_path="/plugins/servlet/customizations-scanner",
            ready_selector="new-scan-btn",
            ready_selector_type="id",
            new_scan_selector="new-scan-btn",
            completed_text="Done",
            scan_timeout=1200,
        ),
    )

    driver = SimpleNamespace(current_url="", page_source="")

    extension_ui.app_specific_action(driver, {})

    assert len(scanner_visits) == 2
    assert len(login_calls) == 2
    assert len(websudo_calls) == 2
    assert scanner_waits == [("id", "new-scan-btn")]
