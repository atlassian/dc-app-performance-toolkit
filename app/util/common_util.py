import datetime
import functools
import requests
from datetime import timedelta
from timeit import default_timer as timer
from packaging import version
from util.conf import TOOLKIT_VERSION

CONF_URL = "https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/conf.py"
VERSION_STR = "TOOLKIT_VERSION"
UNSUPPORTED_VERSION_STR = "UNSUPPORTED_VERSION"


def latest_version():
    try:
        r = requests.get(CONF_URL, UNSUPPORTED_VERSION_STR)
        r.raise_for_status()
        conf = r.text.splitlines()
        version_line = next((line for line in conf if VERSION_STR in line))
        latest_version_str = version_line.split('=')[1].replace("'", "").replace('"', "").strip()
        latest_version_check = version.parse(latest_version_str)
        return latest_version_check
    except requests.exceptions.RequestException as e:
        print(f"Warning: DCAPT check for update failed - {e}")


def unsupported_version():
    try:
        r = requests.get(CONF_URL, UNSUPPORTED_VERSION_STR)
        r.raise_for_status()
        conf = r.text.splitlines()
        unsupported_version_line = next((line for line in conf if UNSUPPORTED_VERSION_STR in line))
        unsupported_version_str = unsupported_version_line.split('=')[1].replace("'", "").replace('"', "").strip()
        unsupported_version_check = version.parse(unsupported_version_str)
        return unsupported_version_check
    except requests.exceptions.RequestException as e:
        print(f"Warning: DCAPT check for update failed - {e}")


def current_version():
    current_version_parse = version.parse(TOOLKIT_VERSION)

    return current_version_parse


def print_timing(message, sep='-'):
    assert message is not None, "Message is not passed to print_timing decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = timer()
            print(sep * 20)
            print(f'{message} started {datetime.datetime.now().strftime("%H:%M:%S")}')
            result = func(*args, **kwargs)
            end = timer()
            print(f"{message} finished in {timedelta(seconds=end - start)}")
            print(sep * 20)
            return result

        return wrapper

    return deco_wrapper
