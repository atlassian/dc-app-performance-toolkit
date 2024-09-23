import datetime
import functools
import requests
from datetime import timedelta
from timeit import default_timer as timer
from packaging import version
from util.conf import TOOLKIT_VERSION

CONF_URL = "https://raw.githubusercontent.com/atlassian/dc-app-performance-toolkit/master/app/util/conf.py"


def get_latest_version(supported=True):
    """
    Get the latest version of DCAPT from the master branch in GIT repository.

    :param supported - version is supported.
    :return: latest version.
    """
    VERSION_STR = "TOOLKIT_VERSION" if supported else "UNSUPPORTED_VERSION"
    try:
        r = requests.get(CONF_URL)
        r.raise_for_status()
        conf = r.text.splitlines()
        version_line = next((line for line in conf if VERSION_STR in line))
        latest_version_str = version_line.split(
            '=')[1].replace("'", "").replace('"', "").strip()
        latest_version = version.parse(latest_version_str)
        return latest_version
    except requests.exceptions.RequestException as e:
        print(f"Warning: DCAPT check for update failed - {e}")
    except StopIteration:
        print("Warning: failed to get the unsupported version")


def get_unsupported_version():
    """
    Get the latest unsupported version of DCAPT from the master branch in GIT repository.

    :return: latest unsupported version.
    """
    unsupported_version_str = get_latest_version(supported=False)

    return unsupported_version_str


def get_current_version():
    """
    Get the DCAPT version from the local repository that the tests were run from.

    :return: local DCAPT version.
    """
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


def webdriver_pretty_debug(webdriver, additional_field):
    debug_message = {}
    for key, value in additional_field.items():
        debug_message[key] = value

    if 'debug_info' in dir(webdriver):
        webdriver.debug_info['current_url'] = webdriver.current_url
        webdriver.debug_info['session_id'] = webdriver.session_id
        debug_message.update(webdriver.debug_info)
    list_to_print = '\n'.join(
        [f'{key}: {value}' for key, value in debug_message.items()])
    pretty_formatted_string = f"""=============== WEBDRIVER DEBUG INFORMATION ===============""" + \
        f'\n{list_to_print}' + """\n===========================================================\n"""
    return pretty_formatted_string
