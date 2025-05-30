import random
from selenium_ui.conftest import print_timing, measure_browser_navi_metrics, measure_dom_requests

from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Page, Dashboard, TopNavPanel, Editor, \
    Logout
from selenium_ui.confluence.pages.selectors import PageLocators
from util.api.confluence_clients import ConfluenceRestClient
from util.confluence.browser_metrics import browser_metrics
from util.conf import CONFLUENCE_SETTINGS

USERS = "users"
PAGES = "pages"
CQLS = "cqls"
CUSTOM_PAGES = "custom_pages"
BLOGS = "blogs"
TWO_WORDS_CQL = 'confluence agreement'
THREE_WORDS_CQL = 'shoulder trip discussion'

def setup_run_data(datasets):
    datasets['current_session'] = {}
    user = random.choice(datasets[USERS])
    page = random.choice(datasets[PAGES])
    if CUSTOM_PAGES in datasets:
        if len(datasets[CUSTOM_PAGES]) > 0:
            custom_page = random.choice(datasets[CUSTOM_PAGES])
            datasets['custom_page_id'] = custom_page[0]
    blog = random.choice(datasets[BLOGS])
    datasets['current_session']['username'] = user[0]
    datasets['current_session']['password'] = user[1]
    datasets['current_session']['page_id'] = page[0]
    datasets['current_session']['blog_id'] = blog[0]

    datasets['current_session']['view_page'] = None
    datasets['current_session']['view_page_cache'] = None
    datasets['current_session']['edit_page'] = None
    datasets['current_session']['edit_page_click'] = None
    datasets['current_session']['create_comment_page'] = None
    datasets['current_session']['view_blog'] = None


def generate_debug_session_info(webdriver, datasets):
    debug_data = datasets['current_session']
    if 'current_url' in dir(webdriver):
        debug_data['current_url'] = webdriver.current_url
    debug_data['custom_page_id'] = datasets.get('custom_page_id')
    return debug_data


def login(webdriver, datasets):
    setup_run_data(datasets)
    rest_client = ConfluenceRestClient(
        CONFLUENCE_SETTINGS.server_url,
        CONFLUENCE_SETTINGS.admin_login,
        CONFLUENCE_SETTINGS.admin_password,
        verify=CONFLUENCE_SETTINGS.secure,
    )
    login_page = Login(webdriver)
    webdriver.debug_info = generate_debug_session_info(webdriver, datasets)

    @print_timing("selenium_login")
    def measure():

        def sub_measure():
            login_page.go_to()
            if login_page.is_logged_in():
                login_page.delete_all_cookies()
                login_page.go_to()
            login_page.wait_for_page_loaded()
            node_id = login_page.get_node_id()
            node_ip = rest_client.get_node_ip(node_id)
            webdriver.node_ip = node_ip
            print(f"node_id:{node_id}, node_ip: {webdriver.node_ip}")
            measure_dom_requests(webdriver, interaction="selenium_login:open_login_page")

        sub_measure()

        login_page.set_credentials(username=datasets['current_session']['username'],
                                   password=datasets['current_session']['password'])

        def sub_measure():
            login_page.click_login_button()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page.wait_for_page_loaded()
            measure_dom_requests(webdriver, interaction="selenium_login:login_and_view_dashboard")
            if CONFLUENCE_SETTINGS.extended_metrics:
                measure_browser_navi_metrics(webdriver, datasets, expected_metrics=browser_metrics['selenium_login'])

        sub_measure()
        current_session_response = login_page.rest_api_get(url=f'{CONFLUENCE_SETTINGS.server_url}'
                                                               f'/rest/api/user/current')
        if 'username' in current_session_response:
            actual_username = current_session_response['username']
            assert actual_username == datasets['current_session']['username']

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_page(webdriver, datasets):
    random_page = random.choice(datasets[PAGES])
    page_id = random_page[0]
    page_description = random_page[2]
    datasets['current_session']['view_page'] = random_page
    datasets['current_session']['view_page_cache'] = random_page
    page = Page(webdriver, page_id=page_id)

    @print_timing("selenium_view_page")
    def measure():
        page.go_to()
        page.wait_for_page_loaded()
        measure_dom_requests(webdriver, interaction=f"selenium_view_page", description=page_description)
        if CONFLUENCE_SETTINGS.extended_metrics:
            measure_browser_navi_metrics(webdriver, datasets, expected_metrics=browser_metrics['selenium_view_page'])

    measure()


def view_page_from_cache(webdriver, datasets):
    cached_page = datasets['current_session']['view_page_cache']
    page_id = cached_page[0]
    page_description = cached_page[2]
    datasets['current_session']['view_page'] = cached_page

    page = Page(webdriver, page_id=page_id)

    @print_timing("selenium_view_page_from_cache")
    def measure():
        page.go_to()
        page.wait_for_page_loaded()
        measure_dom_requests(webdriver, interaction=f"selenium_view_page_from_cache", description=page_description)
        if CONFLUENCE_SETTINGS.extended_metrics:
            measure_browser_navi_metrics(webdriver, datasets,
                                         expected_metrics=browser_metrics['selenium_view_page_from_cache'])

    measure()


def view_blog(webdriver, datasets):
    random_blog = random.choice(datasets[BLOGS])
    blog_id = random_blog[0]
    blog_description = random_blog[2]
    blog = Page(webdriver, page_id=blog_id)
    datasets['current_session']['view_blog'] = random_blog

    @print_timing("selenium_view_blog")
    def measure():
        blog.go_to()
        blog.wait_for_page_loaded()
        measure_dom_requests(webdriver, interaction=f"selenium_view_blog", description=blog_description)
        if CONFLUENCE_SETTINGS.extended_metrics:
            measure_browser_navi_metrics(webdriver, datasets, expected_metrics=browser_metrics['selenium_view_blog'])

    measure()


def view_dashboard(webdriver, datasets):
    dashboard_page = Dashboard(webdriver)

    @print_timing("selenium_view_dashboard")
    def measure():
        dashboard_page.go_to()
        dashboard_page.wait_for_page_loaded()
        measure_dom_requests(webdriver, interaction="selenium_view_dashboard")
        if CONFLUENCE_SETTINGS.extended_metrics:
            measure_browser_navi_metrics(webdriver, datasets,
                                         expected_metrics=browser_metrics['selenium_view_dashboard'])

    measure()


def create_confluence_page(webdriver, datasets):
    nav_panel = TopNavPanel(webdriver)
    create_page = Editor(webdriver)

    @print_timing("selenium_create_page")
    def measure():
        def sub_measure():
            PopupManager(webdriver).dismiss_default_popup()
            nav_panel.click_create()
            PopupManager(webdriver).dismiss_default_popup()
            create_page.wait_for_create_page_open()
            measure_dom_requests(webdriver, interaction="selenium_create_page:open_create_page_editor")
            if CONFLUENCE_SETTINGS.extended_metrics:
                measure_browser_navi_metrics(webdriver, datasets,
                                             expected_metrics=browser_metrics['selenium_create_page'])

        sub_measure()

        PopupManager(webdriver).dismiss_default_popup()

        create_page.write_title()
        create_page.write_content()

        def sub_measure():
            create_page.click_submit()
            page = Page(webdriver)
            page.wait_for_page_loaded()
            measure_dom_requests(webdriver, interaction="selenium_create_page:save_created_page")

        sub_measure()

    measure()


def edit_confluence_page_by_url(webdriver, datasets):
    random_page = random.choice(datasets[PAGES])
    page_id = random_page[0]
    page_description = random_page[2]
    datasets['current_session']['edit_page'] = random_page
    edit_page = Editor(webdriver, page_id=page_id)

    @print_timing("selenium_edit_page_by_url")
    def measure():
        def sub_measure():
            edit_page.go_to()
            edit_page.wait_for_page_loaded()
            measure_dom_requests(webdriver, interaction=f"selenium_edit_page_by_url:open_create_page_editor",
                                 description=page_description)
            if CONFLUENCE_SETTINGS.extended_metrics:
                measure_browser_navi_metrics(webdriver, datasets,
                                             expected_metrics=browser_metrics['selenium_edit_page_by_url'])

        sub_measure()

        edit_page.write_content()

        def sub_measure():
            edit_page.save_edited_page()
            measure_dom_requests(webdriver, interaction=f"selenium_edit_page_by_url:save_edited_page",
                                 description=page_description)

        sub_measure()

    measure()


def edit_confluence_page_quick_edit(webdriver, datasets):
    random_page = datasets['current_session']['edit_page']
    page_description = random_page[2]
    datasets['current_session']['edit_page_click'] = random_page
    page = Page(webdriver, page_id=random_page[0])
    edit_page = Editor(webdriver, page_id=random_page[0])

    @print_timing("selenium_quick_edit_page_click")
    def measure():
        def sub_measure():
            page.go_to()
            page.wait_for_resources_loaded()
            page.wait_for_page_loaded()
            PopupManager(webdriver).dismiss_default_popup()
            page.click_edit()
            edit_page.wait_for_page_loaded()
            measure_dom_requests(webdriver, interaction=f"selenium_quick_edit_page_click:open_create_page_editor",
                                 description=page_description)
            if CONFLUENCE_SETTINGS.extended_metrics:
                measure_browser_navi_metrics(webdriver, datasets,
                                             expected_metrics=browser_metrics['selenium_quick_edit_page_click'])

        sub_measure()

        edit_page.write_content()

        def sub_measure():
            edit_page.save_edited_page()
            measure_dom_requests(webdriver, interaction=f"selenium_quick_edit_page_click:save_edited_page",
                                 description=page_description)

        sub_measure()

    measure()


def create_inline_comment(webdriver, datasets):
    page = random.choice(datasets[PAGES])
    page_id = page[0]
    datasets['current_session']['create_comment_page'] = page
    page = Page(webdriver, page_id=page_id)
    editor_page = Editor(webdriver)

    @print_timing("selenium_create_comment")
    def measure():
        page.go_to()
        page.wait_for_page_loaded()
        PopupManager(webdriver).dismiss_default_popup()

        @print_timing("selenium_create_comment:write_comment")
        def sub_measure():
            page.click_add_comment()
            editor_page.write_content(text='This is selenium comment')

        sub_measure()

        @print_timing("selenium_create_comment:save_comment")
        def sub_measure():
            editor_page.click_submit()
            page.wait_for_comment_field()

        sub_measure()

    measure()

def cql_search_three_words(webdriver):
    return cql_search(webdriver, cql_string=THREE_WORDS_CQL, print_timing_suffix='three_words')


def cql_search_two_words(webdriver):
    return cql_search(webdriver, cql_string=TWO_WORDS_CQL, print_timing_suffix='two_words')


def cql_search(webdriver, cql_string, print_timing_suffix):
    page = Page(webdriver)
    page.wait_until_visible(PageLocators.search_box)
    PopupManager(webdriver).dismiss_default_popup()

    @print_timing(f"selenium_cql_search_{print_timing_suffix}")
    def measure():
        page.get_element(PageLocators.search_box).send_keys(cql_string)
        page.wait_until_any_ec_presented((PageLocators.empty_search_results, PageLocators.search_results),
                                         timeout=30)
        page.get_element(PageLocators.close_search_button).click()
    measure()


def log_out(webdriver, datasets):
    logout_page = Logout(webdriver)
    login_page = Login(webdriver)

    @print_timing("selenium_log_out")
    def measure():
        logout_page.go_to()
        logout_page.wait_for_logout()
        login_page.wait_for_page_loaded()
        login_page.delete_all_cookies()

    measure()
