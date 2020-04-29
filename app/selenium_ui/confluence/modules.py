import random
from selenium_ui.conftest import print_timing

from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Page, Dashboard, TopNavPanel, Editor, \
    Logout


def setup_run_data(datasets):
    user = random.choice(datasets["users"])
    page = random.choice(datasets["pages"])
    blog = random.choice(datasets["blogs"])
    datasets['username'] = user[0]
    datasets['password'] = user[1]
    datasets['page_id'] = page[0]
    datasets['blog_id'] = blog[0]


def login(webdriver, datasets):
    setup_run_data(datasets)
    login_page = Login(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            login_page.go_to()
            login_page.wait_for_page_loaded(interaction)
        measure(webdriver, "selenium_login:open_login_page")

        login_page.set_credentials(username=datasets['username'], password=datasets['password'])

        @print_timing
        def measure(webdriver, interaction):
            login_page.click_login_button(interaction)
            if login_page.is_first_login():
                login_page.first_user_setup(interaction)
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded(interaction)
        measure(webdriver, "selenium_login:login_and_view_dashboard")
    measure(webdriver, 'selenium_login')
    PopupManager(webdriver).dismiss_default_popup()


def view_page(webdriver, datasets):
    page = Page(webdriver, page_id=datasets['page_id'])

    @print_timing
    def measure(webdriver, interaction):
        page.go_to()
        page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_page")


def view_blog(webdriver, datasets):
    blog = Page(webdriver, page_id=datasets['blog_id'])

    @print_timing
    def measure(webdriver, interaction):
        blog.go_to()
        blog.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_blog")


def view_dashboard(webdriver, datasets):
    dashboard_page = Dashboard(webdriver)

    @print_timing
    def measure(webdriver, interaction):
        dashboard_page.go_to()
        dashboard_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_dashboard")


def create_page(webdriver, datasets):
    nav_panel = TopNavPanel(webdriver)
    create_page = Editor(webdriver)

    @print_timing
    def measure(webdriver, interaction):
        nav_panel.click_create(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        create_page.wait_for_create_page_open(interaction)
    measure(webdriver, "selenium_create_page:open_create_page_editor")

    PopupManager(webdriver).dismiss_default_popup()

    create_page.write_title()
    create_page.write_content(interaction='create page')

    @print_timing
    def measure(webdriver, interaction):
        create_page.click_submit()
        page = Page(webdriver)
        page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_create_page:save_created_page")


def edit_page(webdriver, datasets):
    edit_page = Editor(webdriver, page_id=datasets['page_id'])

    @print_timing
    def measure(webdriver, interaction):
        edit_page.go_to()
        edit_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_edit_page:open_create_page_editor")

    edit_page.write_content(interaction='edit page')

    @print_timing
    def measure(webdriver, interaction):
        edit_page.save_edited_page(interaction)
    measure(webdriver, "selenium_edit_page:save_edited_page")


def create_comment(webdriver, datasets):
    page = Page(webdriver, page_id=datasets['page_id'])
    page.go_to()
    page.wait_for_page_loaded(interaction='create comment')
    edit_comment = Editor(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        page.click_add_comment()
        edit_comment.write_content(interaction=interaction, text='This is selenium comment')
    measure(webdriver, 'selenium_create_comment:write_comment')

    @print_timing
    def measure(webdriver, interaction):
        edit_comment.click_submit()
        page.wait_for_comment_field(interaction)
    measure(webdriver, "selenium_create_comment:save_comment")


def log_out(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        logout_page = Logout(webdriver)
        logout_page.go_to()
    measure(webdriver, "selenium_log_out")
