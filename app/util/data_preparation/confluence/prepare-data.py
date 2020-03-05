import random
import string

import urllib3

from util.conf import CONFLUENCE_SETTINGS
from util.data_preparation.api.confluence_clients import ConfluenceRpcClient, ConfluenceRestClient
from util.project_paths import CONFLUENCE_USERS, CONFLUENCE_PAGES, CONFLUENCE_BLOGS

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERS = "users"
PAGES = "pages"
BLOGS = "blogs"
DEFAULT_USER_PREFIX = 'performance_'
DEFAULT_USER_PASSWORD = 'password'


def generate_random_string(length=20):
    return "".join([random.choice(string.ascii_lowercase) for _ in range(length)])


def __create_data_set(rest_client, rpc_client):
    dataset = dict()
    dataset[USERS] = __get_users(rest_client, rpc_client, CONFLUENCE_SETTINGS.concurrency)
    dataset[PAGES] = __get_pages(rest_client, 5000)
    dataset[BLOGS] = __get_blogs(rest_client, 5000)
    return dataset


def __get_users(confluence_api, rpc_api, count):
    cur_perf_users = confluence_api.get_users(DEFAULT_USER_PREFIX, count)
    if len(cur_perf_users) >= count:
        return cur_perf_users

    while len(cur_perf_users) < count:
        username = f"{DEFAULT_USER_PREFIX}{generate_random_string(10)}"
        try:
            user = rpc_api.create_user(username=username, password=DEFAULT_USER_PASSWORD)
            print(f"User {user['name']} is created, number of users to create is "
                  f"{count - len(cur_perf_users)}")
            cur_perf_users.append(user)
        # To avoid rate limit error from server. Execution should not be stopped after catch error from server.
        except Exception as error:
            print(error)
    print('All performance test users were successfully created')
    return cur_perf_users


def __get_pages(confluence_api, count):
    pages = confluence_api.get_content_search(
        0, count, cql='type=page'
                      ' and title !~ JMeter'  # filter out pages created by JMeter
                      ' and title !~ Selenium'  # filter out pages created by Selenium
                      ' and title !~ Home')  # filter out space Home pages
    if not pages:
        raise SystemExit(f"There are no Pages in Confluence")

    return pages


def __get_blogs(confluence_api, count):
    blogs = confluence_api.get_content_search(
        0, count, cql='type=blogpost'
                      ' and title !~ Performance')
    if not blogs:
        raise SystemExit(f"There are no Blog posts in Confluence")

    return blogs


def __is_remote_api_enabled(confluence_api):
    return confluence_api.is_remote_api_enabled()


def __write_to_file(file_path, items):
    with open(file_path, 'w') as f:
        for item in items:
            f.write(f"{item}\n")


def write_test_data_to_files(dataset):
    pages = [f"{page['id']},{page['space']['key']}" for page in dataset[PAGES]]
    __write_to_file(CONFLUENCE_PAGES, pages)

    blogs = [f"{blog['id']},{blog['space']['key']}" for blog in dataset[BLOGS]]
    __write_to_file(CONFLUENCE_BLOGS, blogs)

    users = [f"{user['user']['username']},{DEFAULT_USER_PASSWORD}" for user in dataset[USERS]]
    __write_to_file(CONFLUENCE_USERS, users)


def main():
    print("Started preparing data")

    url = CONFLUENCE_SETTINGS.server_url
    print("Server url: ", url)

    rest_client = ConfluenceRestClient(url, CONFLUENCE_SETTINGS.admin_login, CONFLUENCE_SETTINGS.admin_password)
    rpc_client = ConfluenceRpcClient(url, CONFLUENCE_SETTINGS.admin_login, CONFLUENCE_SETTINGS.admin_password)

    __is_remote_api_enabled(rest_client)

    dataset = __create_data_set(rest_client, rpc_client)
    write_test_data_to_files(dataset)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
