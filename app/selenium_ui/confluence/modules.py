import random
from selenium_ui.conftest import print_timing

from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Page, Dashboard, TopNavPanel, Editor, \
    Logout

USERS = "users"
PAGES = "pages"
CUSTOM_PAGES = "custom_pages"
BLOGS = "blogs"


def setup_run_data(datasets):
    user = random.choice(datasets[USERS])
    page = random.choice(datasets[PAGES])
    if CUSTOM_PAGES in datasets:
        if len(datasets[CUSTOM_PAGES]) > 0:
            custom_page = random.choice(datasets[CUSTOM_PAGES])
            datasets['custom_page_id'] = custom_page[0]
    blog = random.choice(datasets[BLOGS])
    datasets['username'] = user[0]
    datasets['password'] = user[1]
    datasets['page_id'] = page[0]
    datasets['blog_id'] = blog[0]


def login(webdriver, datasets):
    setup_run_data(datasets)
    login_page = Login(webdriver)

    @print_timing("selenium_login")
    def measure():

        @print_timing("selenium_login:open_login_page")
        def sub_measure():
            login_page.go_to()
            if login_page.is_logged_in():
                login_page.delete_all_cookies()
                login_page.go_to()
            login_page.wait_for_page_loaded()
            webdriver.node_id = login_page.get_node_id()
            print(f"node_id:{webdriver.node_id}")
        sub_measure()

        login_page.set_credentials(username=datasets['username'], password=datasets['password'])

        @print_timing("selenium_login:login_and_view_dashboard")
        def sub_measure():
            login_page.click_login_button()
            if login_page.is_first_login():
                login_page.first_user_setup()
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded()
        sub_measure()
    measure()
    PopupManager(webdriver).dismiss_default_popup()


def view_page(webdriver, datasets):
    page = Page(webdriver, page_id=datasets['page_id'])

    @print_timing("selenium_view_page")
    def measure():
        page.go_to()
        page.wait_for_page_loaded()
    measure()


def view_blog(webdriver, datasets):
    blog = Page(webdriver, page_id=datasets['blog_id'])

    @print_timing("selenium_view_blog")
    def measure():
        blog.go_to()
        blog.wait_for_page_loaded()
    measure()


def view_dashboard(webdriver, datasets):
    dashboard_page = Dashboard(webdriver)

    @print_timing("selenium_view_dashboard")
    def measure():
        dashboard_page.go_to()
        dashboard_page.wait_for_page_loaded()
    measure()


def create_confluence_page(webdriver, datasets):
    nav_panel = TopNavPanel(webdriver)
    create_page = Editor(webdriver)

    @print_timing("selenium_create_page")
    def measure():

        @print_timing("selenium_create_page:open_create_page_editor")
        def sub_measure():
            nav_panel.click_create()
            PopupManager(webdriver).dismiss_default_popup()
            create_page.wait_for_create_page_open()
        sub_measure()

        PopupManager(webdriver).dismiss_default_popup()

        create_page.write_title()
        create_page.write_content()

        @print_timing("selenium_create_page:save_created_page")
        def sub_measure():
            create_page.click_submit()
            page = Page(webdriver)
            page.wait_for_page_loaded()
        sub_measure()
    measure()


def edit_confluence_page(webdriver, datasets):
    edit_page = Editor(webdriver, page_id=datasets['page_id'])

    @print_timing("selenium_edit_page")
    def measure():

        @print_timing("selenium_edit_page:open_create_page_editor")
        def sub_measure():
            edit_page.go_to()
            edit_page.wait_for_page_loaded()
        sub_measure()

        edit_page.write_content()

        @print_timing("selenium_edit_page:save_edited_page")
        def sub_measure():
            edit_page.save_edited_page()
        sub_measure()
    measure()


def create_comment(webdriver, datasets):
    page = Page(webdriver, page_id=datasets['page_id'])

    @print_timing("selenium_create_comment")
    def measure():
        page.go_to()
        page.wait_for_page_loaded()
        edit_comment = Editor(webdriver)

        @print_timing("selenium_create_comment:write_comment")
        def sub_measure():
            page.click_add_comment()
            edit_comment.write_content(text='This is selenium comment')
        sub_measure()

        @print_timing("selenium_create_comment:save_comment")
        def sub_measure():
            edit_comment.click_submit()
            page.wait_for_comment_field()
        sub_measure()
    measure()


def log_out(webdriver, datasets):

    @print_timing("selenium_log_out")
    def measure():
        logout_page = Logout(webdriver)
        logout_page.go_to()
        logout_page.wait_for_logout()

    measure()
