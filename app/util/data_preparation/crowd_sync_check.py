import urllib3
from timeit import default_timer as timer
import functools
from datetime import timedelta

from util.conf import CROWD_SETTINGS
from util.api.crowd_clients import CrowdRestClient


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def print_timing(message):
    assert message is not None, "Message is not passed to print_timing decorator"

    def deco_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = timer()
            result = func(*args, **kwargs)
            end = timer()
            print(f"{message}: {timedelta(seconds=end-start)} seconds")
            return result
        return wrapper
    return deco_wrapper


@print_timing('Users synchronization')
def get_users(client):
    users = client.search(start_index=0, max_results='-1', expand='user')
    return users


@print_timing('Users membership synchronization')
def get_users_membership(client):
    membership = client.get_group_membership()
    return membership


if __name__ == "__main__":
    client = CrowdRestClient(CROWD_SETTINGS.server_url, CROWD_SETTINGS.application_name,
                             CROWD_SETTINGS.application_password, verify=CROWD_SETTINGS.secure)
    get_users(client)
    get_users_membership(client)
