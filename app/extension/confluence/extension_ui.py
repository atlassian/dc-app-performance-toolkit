import pytest
from selenium.webdriver.common.by import By

from selenium_ui.base_page import BasePage
from selenium_ui.conftest import print_timing
from util.conf import CONFLUENCE_SETTINGS


_SELECTOR_TYPES = {
    "css": By.CSS_SELECTOR,
    "id": By.ID,
}


def _required_config(value, name):
    if not value:
        raise ValueError(
            f"Customization Insights setting '{name}' is required. "
            "Set it under settings.env.customization_insights in app/confluence.yml."
        )
    return value


def _selector(selector_type, selector_value):
    selector_by = _SELECTOR_TYPES.get((selector_type or "css").lower())
    if not selector_by:
        raise ValueError("Customization Insights selector type must be one of: css, id")
    return selector_by, _required_config(selector_value, "ready_selector/detail_selector")


def _absolute_url(path):
    return f"{CONFLUENCE_SETTINGS.server_url}{_required_config(path, 'ui_path')}"


def app_specific_action(webdriver, datasets):
    config = CONFLUENCE_SETTINGS.customization_insights
    if not config.enabled:
        pytest.skip("Customization Insights action is disabled.")

    page = BasePage(webdriver)

    @print_timing("selenium_customization_insights")
    def measure():
        @print_timing("selenium_customization_insights:open_insights")
        def open_insights():
            page.go_to_url(_absolute_url(config.ui_path))
            page.wait_until_visible(_selector(config.ready_selector_type, config.ready_selector))
            page.wait_for_dom_mutations_complete()

        open_insights()

        if config.detail_path and config.detail_selector:
            @print_timing("selenium_customization_insights:open_detail")
            def open_detail():
                page.go_to_url(_absolute_url(config.detail_path))
                page.wait_until_visible(_selector(config.detail_selector_type, config.detail_selector))
                page.wait_for_dom_mutations_complete()

            open_detail()

    measure()
