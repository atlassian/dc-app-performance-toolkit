import sys

from util.common_util import get_latest_version, get_current_version, get_unsupported_version
from util.analytics.application_info import ApplicationSelector
from util.analytics.analytics import MIN_DEFAULTS
from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, BITBUCKET_SETTINGS, JSM_SETTINGS, BAMBOO_SETTINGS, \
    CROWD_SETTINGS

APPS_SETTINGS = {
    "JIRA": JIRA_SETTINGS,
    "CONFLUENCE": CONFLUENCE_SETTINGS,
    "BITBUCKET":  BITBUCKET_SETTINGS,
    "JSM": JSM_SETTINGS,
    "BAMBOO": BAMBOO_SETTINGS,
    "CROWD": CROWD_SETTINGS,
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
    is_jsm = app_name_upper == "JSM"
    if is_jsm:
        current_concurrency = (app_settings.customers_concurrency, app_settings.agents_concurrency)
    else:
        current_concurrency = app_settings.concurrency

    if (
        (not is_jsm and current_concurrency >= min_defaults['concurrency']) or
        (is_jsm and
         current_concurrency >= (min_defaults['customer_concurrency'], min_defaults['agent_concurrency']))
    ):
        # If the number of processors is less than 4, raise a SystemExit with a warning message.
        if processors < 4:
            raise SystemExit(
                f"ERROR: You are trying to run an enterprise-scale load test with concurrency: {current_concurrency} against the "
                f"instance with a weaker configuration than recommended.\n"
                f"Kindly consider decreasing the `concurrency`/`total_actions_per_hour` in your {app_name_upper.lower()}.yml file if this development environment.\n"
                f"For enterprise-scale load make sure environment has a compliant configuration.\n"
                f"To skip environment compliance check set `environment_compliance_check` variable to False in your {app_name_upper.lower()}.yml file.")


def analyze_application_configuration(app_name):
    app_name_upper = app_name.upper()
    app = ApplicationSelector(app_name).application
    processors = app.processors

    try:
        processors = int(processors)
    except ValueError:
        print("Warning: You are using a server instance for running enterprise-scale load tests.")
        return

    app_settings = APPS_SETTINGS[app_name_upper]
    min_defaults = MIN_DEFAULTS.get(app_name.lower())
    validate_application_config(processors, app_name_upper, app_settings, min_defaults)


def main():
    check_dcapt_version()
    try:
        app_name = sys.argv[1].lower()
    except IndexError:
        raise SystemExit("ERROR: execution_compliance_check.py expects application name as argument")

    # TODO: Add a check for CROWD configuration once the feature with processors is implemented in the product
    if app_name.upper() != "CROWD":
        if app_name.upper() in APPS_SETTINGS:
            app_settings = APPS_SETTINGS[app_name.upper()]
            if app_settings.environment_compliance_check:
                analyze_application_configuration(app_name)
        else:
            raise SystemExit(f'ERROR: Unknown application: {app_name.upper()}. '
                             f'Supported applications are {list(APPS_SETTINGS.keys())}')


if __name__ == "__main__":
    main()
