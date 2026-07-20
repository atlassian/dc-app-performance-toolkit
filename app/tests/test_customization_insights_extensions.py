import sys
from types import ModuleType
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml


APP_DIRECTORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIRECTORY))


class FakeLogger:
    def error(self, message):
        pass


def no_op_measure(interaction):
    return lambda action: action


fake_common_utils = ModuleType("locustio.common_utils")
fake_common_utils.init_logger = lambda **_: FakeLogger()
fake_common_utils.jira_measure = no_op_measure
fake_common_utils.run_as_specific_user = lambda **_: no_op_measure
sys.modules["locustio.common_utils"] = fake_common_utils


fake_jira_modules = ModuleType("selenium_ui.jira.modules")
fake_jira_modules.login = lambda *_: None
fake_jira_modules.view_project_summary = lambda *_: None
sys.modules["selenium_ui.jira.modules"] = fake_jira_modules


from extension.jira import extension_locust as jira_extension_locust
from extension.confluence import extension_ui as confluence_extension_ui
from selenium_ui import jira_ui


def test_confluence_base_profile_disables_customization_insights():
    with (APP_DIRECTORY / "confluence.yml").open() as config_file:
        config = yaml.safe_load(config_file)

    assert config["settings"]["env"]["customization_insights_enabled"] is False


def test_jira_scanner_runs_immediately_after_standard_login(monkeypatch):
    ordered_tests = [
        name
        for name, action in jira_ui.__dict__.items()
        if name.startswith("test_") and callable(action)
    ]

    assert ordered_tests[:3] == [
        "test_0_selenium_a_login",
        "test_0_selenium_b_customizations_scanner",
        "test_1_selenium_view_project_summary",
    ]

    calls = []
    monkeypatch.setattr(jira_ui.modules, "login", lambda *_: calls.append("login"))
    monkeypatch.setattr(
        jira_ui.extension_ui,
        "app_specific_action",
        lambda *_: calls.append("scanner"),
    )
    monkeypatch.setattr(
        jira_ui.modules,
        "view_project_summary",
        lambda *_: calls.append("browse"),
    )

    jira_ui.test_0_selenium_a_login(object(), {}, object())
    jira_ui.test_0_selenium_b_customizations_scanner(object(), {}, object())
    jira_ui.test_1_selenium_view_project_summary(object(), {}, object())

    assert calls == ["login", "scanner", "browse"]


def test_disabled_confluence_scanner_skips_before_plugin_navigation(monkeypatch):
    navigations = []

    class FakePage:
        def __init__(self, webdriver):
            self.webdriver = webdriver

        def go_to_url(self, url):
            navigations.append(url)

    monkeypatch.setattr(confluence_extension_ui, "BasePage", FakePage)
    monkeypatch.setattr(
        confluence_extension_ui,
        "CONFLUENCE_SETTINGS",
        SimpleNamespace(customization_insights=SimpleNamespace(enabled=False)),
    )

    with pytest.raises(pytest.skip.Exception, match="disabled"):
        confluence_extension_ui.app_specific_action(object(), {})

    assert navigations == []


class FakeLocustResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content.encode("utf-8")
        self.failures = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def failure(self, message):
        self.failures.append(message)


class FakeLocust:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def get(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return self.response


def configure_jira_status_action(monkeypatch, expected_text):
    monkeypatch.setattr(
        jira_extension_locust,
        "JIRA_SETTINGS",
        SimpleNamespace(
            customization_insights=SimpleNamespace(
                rest_path="/rest/customization-insights/status",
                rest_assertion=expected_text,
            )
        ),
    )


def test_jira_locust_scanner_accepts_configured_response_text(monkeypatch):
    configure_jira_status_action(monkeypatch, "scan complete")
    response = FakeLocustResponse(200, '{"status":"scan complete"}')
    locust = FakeLocust(response)

    jira_extension_locust.app_specific_action(locust)

    assert response.failures == []
    assert locust.calls == [
        (
            ("/rest/customization-insights/status",),
            {
                "headers": {"Accept": "application/json,text/plain,*/*"},
                "catch_response": True,
            },
        )
    ]


@pytest.mark.parametrize(
    ("status_code", "content"),
    [
        (500, '{"status":"scan complete"}'),
        (200, '{"status":"still running"}'),
    ],
    ids=["non-200", "missing-configured-text"],
)
def test_jira_locust_scanner_marks_bad_response_as_failure(monkeypatch, status_code, content):
    configure_jira_status_action(monkeypatch, "scan complete")
    response = FakeLocustResponse(status_code, content)

    jira_extension_locust.app_specific_action(FakeLocust(response))

    assert len(response.failures) == 1
