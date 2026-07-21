import pytest
import re
from time import sleep
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import AdminPage, Login
from util.conf import JIRA_SETTINGS


_SELECTOR_TYPES = {
    "css": By.CSS_SELECTOR,
    "id": By.ID,
}

_SCAN_START_TIMEOUT = 60
_DURATION_UNITS_IN_SECONDS = {
    "": 1,
    "s": 1,
    "m": 60,
    "h": 60 * 60,
    "d": 24 * 60 * 60,
    "w": 7 * 24 * 60 * 60,
}


class ScanStartError(RuntimeError):
    pass


class ScanCompletionError(RuntimeError):
    pass


def _required_config(value, name):
    if not value:
        raise ValueError(
            f"Customization Insights setting '{name}' is required. "
            "Set it under settings.env.customization_insights in app/jira.yml."
        )
    return value


def _selector(selector_type, selector_value, setting_name):
    selector_by = _SELECTOR_TYPES.get((selector_type or "css").lower())
    if not selector_by:
        raise ValueError("Customization Insights selector type must be one of: css, id")
    return selector_by, _required_config(selector_value, setting_name)


def _absolute_url(path):
    return f"{JIRA_SETTINGS.server_url}{_required_config(path, 'ui_path')}"


def _raise_if_scanner_page_unavailable(webdriver, ui_path):
    page_source = webdriver.page_source or ""
    current_url = getattr(webdriver, "current_url", "")

    if ("/login.jsp" in current_url
            or "permissionViolation=true" in current_url
            or "You must log in to access this page" in page_source):
        raise RuntimeError(
            "Customizations Scanner page redirected to Jira login. "
            "The admin login/websudo session was not accepted before opening "
            f"'{ui_path}'. Current URL: {current_url}"
        )

    if "error404" in page_source or "dead link" in page_source:
        raise ValueError(
            "Customizations Scanner page returned Jira 404/dead link. "
            f"The plugin servlet is not available at '{ui_path}'. "
            "Verify that the Customizations Scanner plugin is installed/enabled "
            "and that customization_insights_ui_path is correct."
        )


def _dismiss_aui_messages(webdriver):
    webdriver.execute_script("""
        document.querySelectorAll('.aui-close-button, .aui-message .icon-close').forEach(function(button) {
            try { button.click(); } catch (e) {}
        });
        document.querySelectorAll('.aui-flag, .aui-message.closeable').forEach(function(message) {
            message.style.display = 'none';
            message.setAttribute('aria-hidden', 'true');
        });
    """)


def _click_new_scan(webdriver, config):
    button_id = _required_config(config.new_scan_selector, "new_scan_selector")
    try:
        button = webdriver.find_element(By.ID, button_id)
        webdriver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", button)
        _dismiss_aui_messages(webdriver)
        try:
            button.click()
        except ElementClickInterceptedException:
            _dismiss_aui_messages(webdriver)
            webdriver.execute_script("arguments[0].click();", button)
    except WebDriverException as exc:
        raise ScanStartError(
            f"Unable to start Customizations Scanner scan by clicking '{button_id}'."
        ) from exc


def _scanner_status(webdriver, config):
    selector = _selector(config.status_selector_type, config.status_selector, "status_selector")
    return webdriver.find_element(*selector).get_attribute("textContent").strip()


def _wait_until_started(webdriver, config):
    def scan_started(_):
        return _scanner_status(webdriver, config) in {
            config.in_progress_text,
            config.completed_text,
        }

    try:
        WebDriverWait(webdriver, _SCAN_START_TIMEOUT).until(scan_started)
    except TimeoutException as exc:
        raise ScanStartError(
            f"Customizations Scanner scan did not start within {_SCAN_START_TIMEOUT} seconds; "
            f"status never reached '{config.in_progress_text}' or '{config.completed_text}'."
        ) from exc


def _wait_until_completed(webdriver, config):
    def scan_done(_):
        return _scanner_status(webdriver, config) == config.completed_text

    try:
        WebDriverWait(webdriver, config.scan_timeout).until(scan_done)
    except TimeoutException as exc:
        raise ScanCompletionError(
            f"Customizations Scanner scan did not complete within {config.scan_timeout} seconds; "
            f"status never reached '{config.completed_text}'."
        ) from exc


def _wait_for_jmeter_ramp_up():
    duration = str(JIRA_SETTINGS.ramp_up).strip()
    match = re.fullmatch(r"(\d+)([smhdw]?)", duration)
    if not match:
        raise ValueError(
            "Jira 'ramp-up' must be an integer optionally followed by one of s, m, h, d, or w. "
            f"Received: '{duration}'."
        )
    sleep(int(match.group(1)) * _DURATION_UNITS_IN_SECONDS[match.group(2)])


@print_timing("selenium_customizations_scanner:full_scan")
def _run_full_scan(webdriver, config):
    _click_new_scan(webdriver, config)
    _wait_until_started(webdriver, config)
    _wait_until_completed(webdriver, config)


def app_specific_action(webdriver, datasets):
    page = BasePage(webdriver)
    config = JIRA_SETTINGS.customization_insights
    if not config.enabled:
        pytest.skip(
            "Customizations Scanner app-specific action is disabled. "
            "Set customization_insights_enabled: true after the plugin is installed and the servlet path is verified."
        )

    @print_timing("selenium_customizations_scanner")
    def measure():
        @print_timing("selenium_customizations_scanner:admin_login")
        def admin_login():
            login_page = Login(webdriver)
            login_page.delete_all_cookies()
            login_page.go_to()
            login_page.wait_for_login_page_loaded()
            login_page.set_credentials(
                username=JIRA_SETTINGS.admin_login,
                password=JIRA_SETTINGS.admin_password
            )
            login_page.wait_for_dashboard_or_first_login_loaded()
            if login_page.is_first_login():
                login_page.first_login_setup()
            if login_page.is_first_login_second_page():
                login_page.first_login_second_page_setup()
            login_page.wait_for_page_loaded()

        @print_timing("selenium_customizations_scanner:websudo")
        def websudo():
            AdminPage(webdriver).go_to(password=JIRA_SETTINGS.admin_password)

        @print_timing("selenium_customizations_scanner:open_scanner")
        def open_scanner():
            for attempt in range(2):
                page.go_to_url(_absolute_url(config.ui_path))
                try:
                    _raise_if_scanner_page_unavailable(webdriver, config.ui_path)
                except RuntimeError:
                    if attempt == 0:
                        admin_login()
                        websudo()
                        continue
                    raise
                page.wait_until_visible(_selector(config.ready_selector_type, config.ready_selector, "ready_selector"))
                page.wait_for_dom_mutations_complete()
                return

        admin_login()
        websudo()
        open_scanner()
        _wait_for_jmeter_ramp_up()
        _run_full_scan(webdriver, config)
        page.wait_for_dom_mutations_complete()

    measure()
