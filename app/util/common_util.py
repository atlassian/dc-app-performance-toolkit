import datetime
import functools
import requests
from datetime import timedelta
from timeit import default_timer as timer
from packaging import version
from util.conf import TOOLKIT_VERSION

CONF_URL = "https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/conf.py"


def get_latest_version(supported=True):
    VERSION_STR = "TOOLKIT_VERSION" if supported else "UNSUPPORTED_VERSION"
    try:
        r = requests.get(CONF_URL)
        r.raise_for_status()
        conf = r.text.splitlines()
        version_line = next((line for line in conf if VERSION_STR in line))
        latest_version_str = version_line.split('=')[1].replace("'", "").replace('"', "").strip()
        latest_version = version.parse(latest_version_str)
        return latest_version
    except requests.exceptions.RequestException as e:
        print(f"Warning: DCAPT check for update failed - {e}")
    except StopIteration:
        print("Warning: failed to get the unsupported version")


def get_unsupported_version():

    unsupported_version_str = get_latest_version(supported=False)

    return unsupported_version_str


def get_current_version():
    return version.parse(TOOLKIT_VERSION)


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
