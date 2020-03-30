import random
import time
import urllib.parse

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

from selenium_ui.conftest import print_timing, AnyEc, generate_random_string
from util.conf import JIRA_SETTINGS

from selenium_ui.jira.pages.pages import LoginPage, PopupManager, IssuePage, ProjectSummary, Search

timeout = 20

ISSUE_TYPE_DROPDOWN = 'issuetype-field'
APPLICATION_URL = JIRA_SETTINGS.server_url


def setup_run_data(datasets):
    user = random.choice(datasets["users"])
    issue = random.choice(datasets["issues"])
    project_key = random.choice(datasets["issues"])[2]
    datasets['username'] = user[0]
    datasets['password'] = user[1]
    datasets['issue_key'] = issue[0]
    datasets['issue_id'] = issue[1]
    datasets['project_key'] = project_key
    datasets['jql'] = urllib.parse.quote(random.choice(datasets["jqls"][0]))


def login(webdriver, datasets):
    setup_run_data(datasets)
    @print_timing
    def measure(webdriver, interaction):
        login_page = LoginPage(webdriver)
        @print_timing
        # TODO do we need this unused argument? Suggest rewriting without using the same function names and inner funcs
        def measure(webdriver, interaction):
            login_page.go_to()
            login_page.at()
        measure(webdriver, "selenium_login:open_login_page")

        @print_timing
        def measure(webdriver, interaction):
            login_page.set_credentials(username=datasets['username'], password=datasets['password'])
            if login_page.is_first_login():
                login_page.first_login_setup(interaction)
        measure(webdriver, "selenium_login:login_and_view_dashboard")
    measure(webdriver, "selenium_login")
    PopupManager(webdriver).dismiss_default_popup()


def view_issue(webdriver, datasets):
    issue = IssuePage(webdriver, issue_key=datasets['issue_key'])
    @print_timing
    def measure(webdriver, interaction):
        issue.go_to()
        issue.wait_issue_title_visible(interaction)
    measure(webdriver, "selenium_view_issue")


def create_issue(webdriver, datasets):
    issue_modal = IssuePage(webdriver)
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
    project = ProjectSummary(webdriver, project_key=datasets['project_key'])

    @print_timing
    def measure(webdriver, interaction):
        project.go_to()
        project.wait_until_summary_visible(interaction)
    measure(webdriver, "selenium_project_summary")


def search_jql(webdriver, datasets):
    search = Search(webdriver, jql=datasets['jql'])

    @print_timing
    def measure(webdriver, interaction):
        search.go_to()
        search.wait_issue_search_presented(interaction)
    measure(webdriver, "selenium_search_jql")


def edit_issue(webdriver, datasets):
    issue = IssuePage(webdriver, issue_id=datasets['issue_id'])

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            issue.go_to_edit_issue(interaction)  # open editor
        measure(webdriver, "selenium_edit_issue:open_edit_issue_form")

        issue.fill_summary_edit()  # edit summary
        issue.fill_description_edit(interaction)  # edit description

        @print_timing
        def measure(webdriver, interaction):
            issue.edit_issue_submit()  # submit edit issue
            issue.wait_issue_title_visible(interaction)
        measure(webdriver, "selenium_edit_issue:save_edit_issue_form")
    measure(webdriver, "selenium_edit_issue")


def save_comment(webdriver, datasets):
    # open comment editor
    issue_id = random.choice(datasets["issues"])[1]

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/secure/AddComment!default.jspa?id={issue_id}')
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "comment-add-submit")), interaction)

        measure(webdriver, "selenium_save_comment:open_comment_form")

        # save editor
        element = webdriver.find_element_by_id('comment')
        text_comment = "Comment from selenium"
        _write_to_text_area(webdriver, element, text_comment, interaction)

        @print_timing
        def measure(webdriver, interaction):
            webdriver.find_element_by_id('comment-add-submit').click()
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "summary-val")), interaction)

        measure(webdriver, "selenium_save_comment:submit_form")

    measure(webdriver, "selenium_save_comment")


def browse_project(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        page_size = 25
        projects_count = len(datasets['project_keys'])
        pages = projects_count // page_size if projects_count % page_size == 0 else projects_count // page_size + 1
        webdriver.get(
            APPLICATION_URL +
            f'/secure/BrowseProjects.jspa?selectedCategory=all&selectedProjectType=all&page={random.randint(1, pages)}')
        _wait_until(webdriver, AnyEc(ec.presence_of_element_located((By.CSS_SELECTOR, "tbody.projects-list")),
                                     ec.presence_of_element_located((By.CLASS_NAME, "none-panel"))
                                     ), interaction)
    measure(webdriver, "selenium_browse_project")


def browse_board(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/secure/ManageRapidViews.jspa')
        _wait_until(webdriver, ec.presence_of_element_located((By.CSS_SELECTOR, "#ghx-content-main table.aui")),
                    interaction)

    measure(webdriver, "selenium_browse_board")

    _dismiss_popup(webdriver, 'aui-inline-dialog-contents .cancel')


def view_backlog_for_scrum_board(webdriver, datasets):
    board_id = random.choice(datasets["scrum_boards"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/secure/RapidBoard.jspa?rapidView={board_id}&view=planning')
        _wait_until(webdriver, ec.presence_of_element_located(
            (By.CSS_SELECTOR, "#ghx-backlog[data-rendered]:not(.browser-metrics-stale)")), interaction)

    measure(webdriver, "selenium_view_scrum_board_backlog")


def view_scrum_board(webdriver, datasets):
    board_id = random.choice(datasets["scrum_boards"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/secure/RapidBoard.jspa?rapidView={board_id}')
        _wait_until(webdriver, ec.presence_of_element_located((By.CSS_SELECTOR, ".ghx-column")), interaction)

    measure(webdriver, "selenium_view_scrum_board")


def view_kanban_board(webdriver, datasets):
    board_id = random.choice(datasets["kanban_boards"])

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/secure/RapidBoard.jspa?rapidView={board_id}')
        _wait_until(webdriver, ec.presence_of_element_located((By.CSS_SELECTOR, ".ghx-column")), interaction)

    measure(webdriver, "selenium_view_kanban_board")


def view_dashboard(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/secure/Dashboard.jspa')
        _wait_until(webdriver, ec.presence_of_element_located((By.CLASS_NAME, "page-type-dashboard")), interaction)

    measure(webdriver, "selenium_view_dashboard")


def log_out(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/logoutconfirm.jsp')
        webdriver.find_element_by_id('confirm-logout-submit').click()
        _wait_until(webdriver, ec.presence_of_element_located((By.CLASS_NAME, "login-link")), interaction)

    measure(webdriver, "selenium_log_out")


def _write_to_text_area(webdriver, element, input_text, interaction):
    # Rich Text Editor
    if "richeditor-cover" in element.get_attribute("class"):
        attribute_id = element.get_attribute("id")
        iframe_xpath = f"//div[textarea[@id='{attribute_id}']]//iframe"
        _wait_until(webdriver, ec.frame_to_be_available_and_switch_to_it((By.XPATH, iframe_xpath)), interaction)
        # Send keys seems flaky when using Rich Text Editor (tinymce). Make the "input_text" small.
        webdriver.find_element_by_id("tinymce").send_keys(input_text)
        webdriver.switch_to.parent_frame()
    # Plain text
    else:
        element.send_keys(input_text)


def _wait_until(webdriver, expected_condition, interaction, time_out=timeout):
    message = f"Interaction: {interaction}. "
    ec_type = type(expected_condition)
    if ec_type == AnyEc:
        conditions_text = ""
        for ecs in expected_condition.ecs:
            conditions_text = conditions_text + " " + f"Condition: {str(ecs)} Locator: {ecs.locator}\n"

        message += f"Timed out after {time_out} sec waiting for one of the conditions: \n{conditions_text}"

    elif ec_type == ec.invisibility_of_element_located:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.target}")

    elif ec_type == ec.frame_to_be_available_and_switch_to_it:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.frame_locator}")

    else:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.locator}")

    return WebDriverWait(webdriver, time_out).until(expected_condition, message=message)
