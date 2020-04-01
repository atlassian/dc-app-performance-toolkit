import random
import urllib.parse

from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Login, PopupManager, Issue, Project, Search, ProjectsList, \
    BoardsList, Board, Dashboard, Logout


def setup_run_data(datasets):
    page_size = 25
    projects_count = len(datasets['project_keys'])
    user = random.choice(datasets["users"])
    issue = random.choice(datasets["issues"])
    scrum_boards = random.choice(datasets["scrum_boards"])
    kanban_boards = random.choice(datasets["kanban_boards"])
    project_key = random.choice(datasets["issues"])[2]
    datasets['username'] = user[0]
    datasets['password'] = user[1]
    datasets['issue_key'] = issue[0]
    datasets['issue_id'] = issue[1]
    datasets['project_key'] = project_key
    datasets['scrum_board_id'] = scrum_boards[0]
    datasets['kanban_board_id'] = kanban_boards[0]
    datasets['jql'] = urllib.parse.quote(random.choice(datasets["jqls"][0]))
    datasets['pages'] = projects_count // page_size if projects_count % page_size == 0 \
        else projects_count // page_size + 1


def login(webdriver, datasets):
    setup_run_data(datasets)
    @print_timing
    def measure(webdriver, interaction):
        login_page = Login(webdriver)
        @print_timing
        # TODO do we need this unused argument? Suggest rewriting without using the same function names and inner funcs
        def measure(webdriver, interaction):
            login_page.go_to()
        measure(webdriver, "selenium_login:open_login_page")

        @print_timing
        def measure(webdriver, interaction):
            login_page.set_credentials(username=datasets['username'], password=datasets['password'])
            if login_page.is_first_login():
                login_page.first_login_setup(interaction)
            login_page.wait_for_page_loaded(interaction)
        measure(webdriver, "selenium_login:login_and_view_dashboard")
    measure(webdriver, "selenium_login")
    PopupManager(webdriver).dismiss_default_popup()


def view_issue(webdriver, datasets):
    issue_page = Issue(webdriver, issue_key=datasets['issue_key'])
    @print_timing
    def measure(webdriver, interaction):
        issue_page.go_to()
        issue_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_issue")


def create_issue(webdriver, datasets):
    issue_modal = Issue(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            issue_modal.open_create_issue_modal(interaction)
        measure(webdriver, "selenium_create_issue:open_quick_create")

        @print_timing
        def measure(webdriver, interaction):
            issue_modal.fill_summary_create(interaction)  # Fill summary field
            issue_modal.fill_description_create(interaction)  # Fill description field
            issue_modal.assign_to_me()  # Click assign to me
            issue_modal.set_resolution()  # Set resolution if there is such field
            issue_modal.set_issue_type(interaction)  # Set issue type, use non epic type

            @print_timing
            def measure(webdriver, interaction):
                issue_modal.submit_issue(interaction)
            measure(webdriver, "selenium_create_issue:submit_issue_form")
        measure(webdriver, "selenium_create_issue:fill_and_submit_issue_form")
    measure(webdriver, "selenium_create_issue")
    PopupManager(webdriver).dismiss_default_popup()


def view_project_summary(webdriver, datasets):
    project_page = Project(webdriver, project_key=datasets['project_key'])

    @print_timing
    def measure(webdriver, interaction):
        project_page.go_to()
        project_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_project_summary")


def search_jql(webdriver, datasets):
    search_page = Search(webdriver, jql=datasets['jql'])

    @print_timing
    def measure(webdriver, interaction):
        search_page.go_to()
        search_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_search_jql")


def edit_issue(webdriver, datasets):
    issue_page = Issue(webdriver, issue_id=datasets['issue_id'])

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            issue_page.go_to_edit_issue(interaction)  # open editor
        measure(webdriver, "selenium_edit_issue:open_edit_issue_form")

        issue_page.fill_summary_edit()  # edit summary
        issue_page.fill_description_edit(interaction)  # edit description

        @print_timing
        def measure(webdriver, interaction):
            issue_page.edit_issue_submit()  # submit edit issue
            issue_page.wait_for_issue_title(interaction)
        measure(webdriver, "selenium_edit_issue:save_edit_issue_form")
    measure(webdriver, "selenium_edit_issue")


def save_comment(webdriver, datasets):
    issue_page = Issue(webdriver, issue_id=datasets['issue_id'])
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            issue_page.go_to_edit_comment(interaction)  # Open edit comment page
        measure(webdriver, "selenium_save_comment:open_comment_form")

        issue_page.fill_comment_edit(interaction)  # Fill comment text field

        @print_timing
        def measure(webdriver, interaction):
            issue_page.edit_comment_submit(interaction)  # Submit comment
        measure(webdriver, "selenium_save_comment:submit_form")
    measure(webdriver, "selenium_save_comment")


def browse_projects_list(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        projects_list_page = ProjectsList(webdriver, projects_list_pages=datasets['pages'])
        projects_list_page.go_to()
        projects_list_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_browse_projects_list")


def browse_boards_list(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        boards_list_page = BoardsList(webdriver)
        boards_list_page.go_to()
        boards_list_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_browse_boards_list")
    PopupManager(webdriver).dismiss_default_popup()


def view_backlog_for_scrum_board(webdriver, datasets):
    scrum_board_page = Board(webdriver, board_id=datasets['scrum_board_id'])
    @print_timing
    def measure(webdriver, interaction):
        scrum_board_page.go_to_backlog()
        scrum_board_page.wait_for_scrum_board_backlog(interaction)
    measure(webdriver, "selenium_view_scrum_board_backlog")


def view_scrum_board(webdriver, datasets):
    scrum_board_page = Board(webdriver, board_id=datasets['scrum_board_id'])
    @print_timing
    def measure(webdriver, interaction):
        scrum_board_page.go_to()
        scrum_board_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_scrum_board")


def view_kanban_board(webdriver, datasets):
    kanban_board_page = Board(webdriver, board_id=datasets['kanban_board_id'])
    @print_timing
    def measure(webdriver, interaction):
        kanban_board_page.go_to()
        kanban_board_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_kanban_board")


def view_dashboard(webdriver, datasets):
    dashboard_page = Dashboard(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        dashboard_page.go_to()
        dashboard_page.wait_dashboard_presented(interaction)
    measure(webdriver, "selenium_view_dashboard")


def log_out(webdriver, datasets):
    logout_page = Logout(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        logout_page.go_to()
        logout_page.click_logout()
        logout_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_log_out")

