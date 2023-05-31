import sys

from util.common_util import get_latest_version, get_current_version, get_unsupported_version
from util.analytics.analytics_utils import get_first_elem
from util.analytics.application_info import ApplicationSelector
from util.analytics.analytics import MIN_DEFAULTS
from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, BITBUCKET_SETTINGS, JSM_SETTINGS

APPS_SETTINGS = {
    "JIRA": {"settings": JIRA_SETTINGS, 'processors': 6},
    "CONFLUENCE": {"settings": CONFLUENCE_SETTINGS, 'processors': 4},
    "BITBUCKET": {"settings": BITBUCKET_SETTINGS, 'processors': 4},
    "JSM": {"settings": JSM_SETTINGS, 'processors': 6}
}


def check_dcapt_version():
    latest_version = get_latest_version()
    current_version = get_current_version()
    unsupported_version = get_unsupported_version()

    if latest_version is None:
        print('Warning: failed to get the latest version')
    elif unsupported_version is None:
        print('Warning: failed to get the unsupported version')
    elif current_version <= unsupported_version:
        raise SystemExit(f"DCAPT version {current_version} is no longer supported. "
                         f"Consider an upgrade to the latest version: {latest_version}")
    elif current_version < latest_version:
        print(f"Warning: DCAPT version {current_version} is outdated. "
              f"Consider upgrade to the latest version: {latest_version}.")
    elif current_version == latest_version:
        print(f"Info: DCAPT version {current_version} is the latest.")
    else:
        print(f"Info: DCAPT version {current_version} "
              f"is ahead of the latest production version: {latest_version}.")


def validate_application_config(processors, app_name_upper, app_settings, min_defaults):
    is_jsm_or_insight = app_name_upper in ["JSM", "INSIGHT"]

    if ((not is_jsm_or_insight and app_settings.concurrency == min_defaults['concurrency']) or
            (is_jsm_or_insight and
             app_settings.customers_concurrency == min_defaults['customer_concurrency'] and
             app_settings.agents_concurrency == min_defaults['agent_concurrency'])):
        if processors < APPS_SETTINGS[app_name_upper]['processors']:
            raise SystemExit("You are using enterprise-scale load against a development environment. "
                             "Please check your instance configurations or decrease the load.")


def analyze_application_configuration(app_name):
    app_name_upper = app_name.upper()
    if app_name_upper in APPS_SETTINGS:
        app = ApplicationSelector(app_name).application
        deployment_type = app.deployment
        processors = int(app.processors)

        app_settings = APPS_SETTINGS[app_name_upper]["settings"]
        min_defaults = MIN_DEFAULTS.get(app_name.lower())

        if deployment_type == "terraform":
            validate_application_config(processors, app_name_upper, app_settings, min_defaults)


def main():
    check_dcapt_version()
    app_name = get_first_elem(sys.argv)
    analyze_application_configuration(app_name)


if __name__ == "__main__":
    main()
