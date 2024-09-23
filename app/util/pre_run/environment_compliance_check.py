import subprocess
import sys

from packaging import version
from selenium import webdriver

from util.analytics.analytics import MIN_DEFAULTS
from util.analytics.application_info import ApplicationSelector
from util.common_util import get_latest_version, get_current_version, get_unsupported_version
from util.conf import JIRA_SETTINGS, CONFLUENCE_SETTINGS, BITBUCKET_SETTINGS, JSM_SETTINGS, BAMBOO_SETTINGS, \
    CROWD_SETTINGS

APPS_SETTINGS = {
    "JIRA": JIRA_SETTINGS,
    "CONFLUENCE": CONFLUENCE_SETTINGS,
    "BITBUCKET": BITBUCKET_SETTINGS,
    "JSM": JSM_SETTINGS,
    "BAMBOO": BAMBOO_SETTINGS,
    "CROWD": CROWD_SETTINGS,
}

SUPPORTED_JAVA_VERSIONS = [17, 21]


def check_dcapt_version():
    latest_version = get_latest_version()
    current_version = get_current_version()
    unsupported_version = get_unsupported_version()

    if latest_version is None:
        print('WARNING: failed to get the latest version')
    elif unsupported_version is None:
        print('WARNING: failed to get the unsupported version')
    elif current_version <= unsupported_version:
        raise SystemExit(
            f"DCAPT version {current_version} is no longer supported. "
            f"Consider an upgrade to the latest version: {latest_version}")
    elif current_version < latest_version:
        print(f"WARNING: DCAPT version {current_version} is outdated. "
              f"Consider upgrade to the latest version: {latest_version}.")
    elif current_version == latest_version:
        print(f"INFO: DCAPT version {current_version} is the latest.")
    else:
        print(f"INFO: DCAPT version {current_version} "
              f"is ahead of the latest production version: {latest_version}.")


def validate_application_config(
        processors,
        app_name_upper,
        app_settings,
        min_defaults):
    is_jsm = app_name_upper == "JSM"
    if is_jsm:
        current_concurrency = (
            app_settings.customers_concurrency,
            app_settings.agents_concurrency)
    else:
        current_concurrency = app_settings.concurrency

    if (
        (not is_jsm and current_concurrency >= min_defaults['concurrency']) or
        (is_jsm and
         current_concurrency >= (min_defaults['customer_concurrency'], min_defaults['agent_concurrency']))
    ):
        # If the number of processors is less than 4, raise a SystemExit with a
        # warning message.
        if processors < 4:
            raise SystemExit(
                f"ERROR: You are trying to run an enterprise-scale load test with concurrency: "
                f"{current_concurrency} against the instance with a weaker configuration than recommended.\n"
                f"Kindly consider decreasing the `concurrency`/`total_actions_per_hour` in your "
                f"{app_name_upper.lower()}.yml file if this development environment.\n"
                f"For enterprise-scale load make sure environment has a compliant configuration.\n"
                f"To skip environment compliance check set `environment_compliance_check` variable to False in your "
                f"{app_name_upper.lower()}.yml file.")


def validate_chromedriver_version(app_name, app_settings):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    current_chrome_version = version.parse(driver.capabilities['browserVersion'])
    if app_settings.chromedriver_version:
        current_chromedriver_version = version.parse(app_settings.chromedriver_version)
    else:
        print(f"WARNING: Chromedriver version was not found in the {app_name}.yml. Skipping Chrome/chromedriver check.")
        return
    if current_chromedriver_version.major == current_chrome_version.major:
        print(f"INFO: Chrome version: {current_chrome_version}")
        print(f"INFO: Chromedriver version in {app_name}.yml: {current_chromedriver_version}")
    else:
        raise SystemExit(
            f'ERROR: Your Chromedriver version {current_chromedriver_version} is '
            f'not corresponding to your Chrome browser version {current_chrome_version}. '
            f'Please change `chromedriver` version in your {app_name}.yml.')


def validate_java_version():
    try:
        response = subprocess.check_output(['java', '-version'], stderr=subprocess.STDOUT)
        java_version = str(response.splitlines()[0]).split('"')[1]
        print(f'INFO: Java version: {java_version}')
    except Exception as e:
        print(f"WARNING: Skipping Java version check. Failed to get java version: {e}")
        return
    java_version_major = int(java_version.split(".")[0])

    if java_version_major not in SUPPORTED_JAVA_VERSIONS:
        raise SystemExit(
            f"ERROR: Current java version {java_version} is not supported. "
            f"Supported java versions: {SUPPORTED_JAVA_VERSIONS}")


def analyze_application_configuration(app_name, app_settings):
    app_name_upper = app_name.upper()
    app = ApplicationSelector(app_name).application

    print(f"INFO: application_protocol (http or https): {app_settings.protocol}")
    print(f"INFO: application_hostname (should be without protocol, postfix and slash): {app_settings.hostname}")
    print(f"INFO: application_port: {app_settings.port}")
    print(f"INFO: application_postfix: {app_settings.postfix}")
    url = f"{app_settings.protocol}://{app_settings.hostname}:{app_settings.port}{app_settings.postfix}"
    print(f"INFO: Product URL: {url}")

    try:
        status = app.status
        if status:
            print(f"INFO: Product status: {status}")
    except Exception as e:
        raise SystemExit(f"ERROR: check correctness of protocol, hostname, port, postfix in {app_name}.yml file: {url}"
                         f"\n    application_protocol (http or https): {app_settings.protocol}"
                         f"\n    application_hostname (should be without protocol, postfix and slash): "
                         f"{app_settings.hostname}"
                         f"\n    application_port: {app_settings.port}"
                         f"\n    application_postfix: {app_settings.postfix}"
                         f"\n    product URL: {url}"
                         f"\n    Exception: {e}"
                         )

    # TODO: Add a check for CROWD configuration once the feature with
    # processors api is implemented in the product
    if app_name_upper == "CROWD":
        print("Warning: skip processors validation for crowd")
        return

    processors = app.processors
    print(f"INFO: {app_name} processors count: {processors}")

    try:
        processors = int(processors)
        min_defaults = MIN_DEFAULTS.get(app_name.lower())
        validate_application_config(
            processors,
            app_name_upper,
            app_settings,
            min_defaults)
    except ValueError:
        print("WARNING: Skipping processor count validation. Get processor count failed.")

    if app_name.upper() == "CROWD":
        print("INFO: Skipping Chromedriver check for Crowd.")
    else:
        validate_chromedriver_version(app_name, app_settings)

    validate_java_version()


def main():
    check_dcapt_version()
    try:
        app_name = sys.argv[1].lower()
    except IndexError:
        raise SystemExit("ERROR: execution_compliance_check.py expects application name as argument")

    if app_name.upper() in APPS_SETTINGS:
        app_settings = APPS_SETTINGS[app_name.upper()]
        if app_settings.environment_compliance_check:
            analyze_application_configuration(app_name, app_settings)
    else:
        raise SystemExit(
            f'ERROR: Unknown application: {app_name.upper()}. '
            f'Supported applications are {list(APPS_SETTINGS.keys())}')


if __name__ == "__main__":
    main()
