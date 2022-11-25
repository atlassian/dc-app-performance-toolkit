import random
from multiprocessing.pool import ThreadPool

import urllib3

from prepare_data_common import __generate_random_string, __write_to_file
from util.api.confluence_clients import ConfluenceRpcClient, ConfluenceRestClient
from util.common_util import print_timing
from util.conf import CONFLUENCE_SETTINGS
from util.project_paths import CONFLUENCE_USERS, CONFLUENCE_PAGES, CONFLUENCE_BLOGS, CONFLUENCE_CUSTOM_PAGES

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USERS = "users"
PAGES = "pages"
CUSTOM_PAGES = "custom_pages"
BLOGS = "blogs"
DEFAULT_USER_PREFIX = 'performance_'
DEFAULT_USER_PASSWORD = 'password'
ERROR_LIMIT = 10
DATASET_PAGES_TEMPLATES = {'big_attachments_1': ['PAGE_1', 'PAGE_2'],
                           'small_attachments_3': ['PAGE_3', 'PAGE_4', 'PAGE_5', 'PAGE_6'],
                           'small_text_7': ['PAGE_7', 'PAGE_8', 'PAGE_9', 'PAGE_10', 'PAGE_11',
                                            'PAGE_12', 'PAGE_13', 'PAGE_14', 'PAGE_15'],
                           'medium_text_16': ['PAGE_16', 'PAGE_17', 'PAGE_18', 'PAGE_19', 'PAGE_20',
                                              'PAGE_23', 'PAGE_24'],
                           'text_formatting_21': ['PAGE_21', 'PAGE_22', 'PAGE_25', 'PAGE_26', 'PAGE_27', 'PAGE_28',
                                                  'PAGE_29', 'PAGE_30']
                           }
DATASET_BLOGS_TEMPLATES = {1: ['BLOG_1'],  #, 'BLOG_2'], # TODO Investigate how to group similar blogs
                           3: ['BLOG_3'],  #'BLOG_4', 'BLOG_5'],
                           6: ['BLOG_6']  # 'BLOG_7', 'BLOG_8', 'BLOG_9', 'BLOG_10']

                           }
DEFAULT_TEMPLATE_ID = 1

ENGLISH_US = 'en_US'
ENGLISH_GB = 'en_GB'


@print_timing('Creating dataset started')
def __create_data_set(rest_client, rpc_client):
    dataset = dict()
    dataset[USERS] = __get_users(rest_client, rpc_client, CONFLUENCE_SETTINGS.concurrency)
    perf_user = random.choice(dataset[USERS])['user']
    perf_user_api = ConfluenceRestClient(CONFLUENCE_SETTINGS.server_url, perf_user['username'], DEFAULT_USER_PASSWORD)

    pool = ThreadPool(processes=2)
    async_pages = pool.apply_async(__get_pages, (perf_user_api, 5000))
    async_blogs = pool.apply_async(__get_blogs, (perf_user_api, 5000))

    async_pages.wait()
    async_blogs.wait()

    dataset[PAGES] = async_pages.get()
    dataset[BLOGS] = async_blogs.get()

    dataset[CUSTOM_PAGES] = __get_custom_pages(perf_user_api, 5000, CONFLUENCE_SETTINGS.custom_dataset_query)
    print(f'Users count: {len(dataset[USERS])}')
    print(f'Pages count: {len(dataset[PAGES])}')
    print(f'Blogs count: {len(dataset[BLOGS])}')
    print('------------------------')
    print(f'Custom pages count: {len(dataset[CUSTOM_PAGES])}')
    return dataset


@print_timing('Getting users')
def __get_users(confluence_api, rpc_api, count):
    errors_count = 0
    cur_perf_users = confluence_api.get_users(DEFAULT_USER_PREFIX, count)
    if len(cur_perf_users) >= count:
        return cur_perf_users

    while len(cur_perf_users) < count:
        if errors_count >= ERROR_LIMIT:
            raise Exception(f'Maximum error limit reached {errors_count}/{ERROR_LIMIT}. '
                            f'Please check the errors in bzt.log')
        username = f"{DEFAULT_USER_PREFIX}{__generate_random_string(10)}"
        try:
            user = rpc_api.create_user(username=username, password=DEFAULT_USER_PASSWORD)
            print(f"User {user['user']['username']} is created, number of users to create is "
                  f"{count - len(cur_perf_users)}")
            cur_perf_users.append(user)
        # To avoid rate limit error from server. Execution should not be stopped after catch error from server.
        except Exception as error:
            print(f"Warning: Create confluence user error: {error}. Retry limits {errors_count}/{ERROR_LIMIT}")
            errors_count = errors_count + 1
    print('All performance test users were successfully created')
    return cur_perf_users


@print_timing('Getting pages')
def __get_pages(confluence_api, count):
    pages_templates = [i for sublist in DATASET_PAGES_TEMPLATES.values() for i in sublist]
    pages_templates_count = len(pages_templates)
    pages_per_template = int(count / pages_templates_count) if count > pages_templates_count else 1
    dcapt_dataset = bool(confluence_api.search(limit=100, cql='type=page and text ~ PAGE_1'))
    total_pages = []

    if dcapt_dataset:
        for template_id, pages_marks in DATASET_PAGES_TEMPLATES.items():
            for mark in pages_marks:
                pages = confluence_api.get_content_search(
                    0, pages_per_template, cql='type=page'
                                               ' and title !~ JMeter'  # filter out pages created by JMeter
                                               ' and title !~ Selenium'  # filter out pages created by Selenium
                                               ' and title !~ locust'  # filter out pages created by locust
                                               ' and title !~ Home'  # filter out space Home pages
                                               f' and text ~ {mark}')
                for page in pages:
                    page['template_id'] = template_id
                total_pages.extend(pages)

    else:
        total_pages = confluence_api.get_content_search(
            0, count, cql='type=page'
                          ' and title !~ JMeter'  # filter out pages created by JMeter
                          ' and title !~ Selenium'  # filter out pages created by Selenium
                          ' and title !~ locust'  # filter out pages created by locust
                          ' and title !~ Home')  # filter out space Home pages
        for page in total_pages:
            page['template_id'] = DEFAULT_TEMPLATE_ID
    if not total_pages:
        raise SystemExit(f"There are no Pages in Confluence accessible by a random performance user: "
                         f"{confluence_api.user}")

    return total_pages


@print_timing('Getting custom pages')
def __get_custom_pages(confluence_api, count, cql):
    pages = []
    if cql:
        pages = confluence_api.get_content_search(
            0, count, cql=cql)
        if not pages:
            raise SystemExit(f"ERROR: There are no pages in Confluence could be found with CQL: {cql}")
    return pages


@print_timing('Getting blogs')
def __get_blogs(confluence_api, count):
    blogs_templates = [i for sublist in DATASET_BLOGS_TEMPLATES.values() for i in sublist]
    blogs_templates_count = len(blogs_templates)
    blogs_per_template = int(count / blogs_templates_count) if count > blogs_templates_count else 1
    dcapt_dataset = bool(confluence_api.search(limit=100, cql='type=page and text ~ PAGE_1'))
    total_blogs = []

    if dcapt_dataset:
        for template_id, blogs_marks in DATASET_BLOGS_TEMPLATES.items():
            for mark in blogs_marks:
                blogs = confluence_api.get_content_search(
                    0, blogs_per_template, cql='type=blogpost'
                                               ' and title !~ Performance'
                                               f' and text ~ {mark}')
                for blog in blogs:
                    blog['template_id'] = template_id
                total_blogs.extend(blogs)
    else:
        total_blogs = confluence_api.get_content_search(
            0, count, cql='type=blogpost'
                          ' and title !~ Performance')
        for blog in total_blogs:
            blog['template_id'] = DEFAULT_TEMPLATE_ID

    if not total_blogs:
        raise SystemExit(f"There are no Blog posts in Confluence accessible by a random performance user: "
                         f"{confluence_api.user}")

    return total_blogs


def __is_remote_api_enabled(confluence_api):
    return confluence_api.is_remote_api_enabled()


@print_timing('Started writing data to files')
def write_test_data_to_files(dataset):
    pages = [f"{page['id']},{page['space']['key']},{page['template_id']}" for page in dataset[PAGES]]
    __write_to_file(CONFLUENCE_PAGES, pages)

    blogs = [f"{blog['id']},{blog['space']['key']},{blog['template_id']}" for blog in dataset[BLOGS]]
    __write_to_file(CONFLUENCE_BLOGS, blogs)

    users = [f"{user['user']['username']},{DEFAULT_USER_PASSWORD}" for user in dataset[USERS]]
    __write_to_file(CONFLUENCE_USERS, users)

    custom_pages = [f"{page['id']},{page['space']['key']}" for page in dataset[CUSTOM_PAGES]]
    __write_to_file(CONFLUENCE_CUSTOM_PAGES, custom_pages)


def __is_collaborative_editing_enabled(confluence_api):
    status = confluence_api.get_collaborative_editing_status()
    if not all(status.values()):
        raise Exception('Please turn on collaborative editing in Confluence System Preferences page '
                        'in order to run DC Apps Performance Toolkit.')


def __check_current_language(confluence_api):
    language = confluence_api.get_locale()
    if language and language not in [ENGLISH_US, ENGLISH_GB]:
        raise SystemExit(f'"{language}" language is not supported. '
                         f'Please change your profile language to "English (US)"')


def __check_for_admin_permissions(confluence_api):
    groups = confluence_api.get_groups_membership(CONFLUENCE_SETTINGS.admin_login)
    if 'confluence-administrators' not in groups:
        raise SystemExit(f"The '{confluence_api.user}' user does not have admin permissions.")


@print_timing('Confluence data preparation')
def main():
    print("Started preparing data")

    url = CONFLUENCE_SETTINGS.server_url
    print("Server url: ", url)

    rest_client = ConfluenceRestClient(url, CONFLUENCE_SETTINGS.admin_login, CONFLUENCE_SETTINGS.admin_password,
                                       verify=CONFLUENCE_SETTINGS.secure)
    rpc_client = ConfluenceRpcClient(url, CONFLUENCE_SETTINGS.admin_login, CONFLUENCE_SETTINGS.admin_password)
    __is_remote_api_enabled(rest_client)
    __check_for_admin_permissions(rest_client)
    __is_collaborative_editing_enabled(rest_client)
    __check_current_language(rest_client)

    dataset = __create_data_set(rest_client, rpc_client)
    write_test_data_to_files(dataset)

    print("Finished preparing data")


if __name__ == "__main__":
    main()
