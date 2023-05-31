import sys
from sys import version_info

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

SUPPORTED_PYTHON_VERSIONS = ["3.8", "3.9", "3.10", "3.11"]

python_full_version = '.'.join(map(str, version_info[0:3]))
python_short_version = '.'.join(map(str, version_info[0:2]))
print("Python version: {}".format(python_full_version))
if python_short_version not in SUPPORTED_PYTHON_VERSIONS:
    raise SystemExit("Python version {} is not supported. "
                     "Supported versions: {}.".format(python_full_version, SUPPORTED_PYTHON_VERSIONS))

# Print toolkit version after Python check
from util.conf import TOOLKIT_VERSION  # noqa E402

print("Data Center App Performance Toolkit version: {}".format(TOOLKIT_VERSION))


def get_application_info(app_name):
    app_name_upper = app_name.upper()
    if app_name_upper in APPS_SETTINGS:
        app = ApplicationSelector(app_name).application
        deployment_type = app.deployment
        processors = int(app.processors)

        app_settings = APPS_SETTINGS[app_name_upper]["settings"]
        min_defaults = MIN_DEFAULTS.get(app_name.lower())

        if deployment_type == "terraform":
            check_config(processors, app_name_upper, app_settings, min_defaults)


def check_config(processors, app_name_upper, app_settings, min_defaults):
    is_jsm_or_insight = app_name_upper in ["JSM", "INSIGHT"]

    if ((not is_jsm_or_insight and app_settings.concurrency == min_defaults['concurrency']) or
            (is_jsm_or_insight and
             app_settings.customers_concurrency == min_defaults['customer_concurrency'] and
             app_settings.agents_concurrency == min_defaults['agent_concurrency'])):
        if processors < APPS_SETTINGS[app_name_upper]['processors']:
            raise SystemExit("You are using enterprise-scale load against a development environment. "
                             "Please check your instance configurations or decrease the load.")


def main():
    app_name = get_first_elem(sys.argv)
    get_application_info(app_name)


if __name__ == "__main__":
    main()
