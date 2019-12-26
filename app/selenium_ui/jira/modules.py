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

timeout = 20

ISSUE_TYPE_DROPDOWN = 'issuetype-field'
APPLICATION_URL = JIRA_SETTINGS.server_url


def _dismiss_popup(webdriver, *args):
    for elem in args:
        try:
            webdriver.execute_script(f"document.querySelector(\'{elem}\').click()")
        except:
            pass


def login(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        # TODO do we need this unused argument? Suggest rewriting without using the same function names and inner funcs
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/login.jsp')

        measure(webdriver, "selenium_login:open_login_page")

        def _setup_page_is_presented():
            elems = webdriver.find_elements_by_id('next')
            return True if elems else False

        def _user_setup():
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "next")), interaction)
            next_el = webdriver.find_element_by_id('next')
            next_el.send_keys(Keys.ESCAPE)
            next_el.click()
            _wait_until(webdriver,
                        ec.visibility_of_element_located((By.CSS_SELECTOR, "input[value='Next']")), interaction
                        ).click()
            _wait_until(webdriver,
                        ec.visibility_of_element_located((By.CSS_SELECTOR, "a[data-step-key='browseprojects']")),
                        interaction
                        ).click()
            webdriver.get(f'{APPLICATION_URL}/secure/Dashboard.jspa')

        user = random.choice(datasets["users"])
        webdriver.find_element_by_id('login-form-username').send_keys(user[0])
        webdriver.find_element_by_id('login-form-password').send_keys(user[1])

        @print_timing
        def measure(webdriver, interaction):
            webdriver.find_element_by_id('login-form-submit').click()
            if _setup_page_is_presented():
                _user_setup()
            _wait_until(webdriver, ec.presence_of_element_located((By.CLASS_NAME, "page-type-dashboard")), interaction)

        measure(webdriver, "selenium_login:login_and_view_dashboard")

    measure(webdriver, "selenium_login")

    _dismiss_popup(webdriver,
                   '.aui-message .icon-close',
                   'form.tip-footer>.helptip-close',
                   '.aui-inline-dialog-contents .cancel'
                   )


def view_issue(webdriver, datasets):
    issue = random.choice(datasets["issues"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/browse/{issue}')
        _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "summary-val")), interaction)

    measure(webdriver, "selenium_view_issue")


def create_issue(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        # open quick create
        _wait_until(webdriver, ec.element_to_be_clickable((By.ID, "create_link")), interaction)

        @print_timing
        def measure(webdriver, interaction):
            webdriver.find_element_by_id('create_link').click()
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "create-issue-dialog")), interaction)

        measure(webdriver, "selenium_create_issue:open_quick_create")

        # create issue
        @print_timing
        def measure(webdriver, interaction):
            _wait_until(webdriver, ec.element_to_be_clickable((By.ID, "summary")), interaction
                        ).send_keys(f"Issue created date {time.time()}")

            text_description = f'Description: {generate_random_string(100)}'
            element = webdriver.find_element_by_id('description')
            _write_to_text_area(webdriver, element, text_description, interaction)

            # Assign to me
            assign_els = webdriver.find_elements_by_id('assign-to-me-trigger')
            if assign_els:
                assign_els[0].click()

            # Set resolution if there is such field
            resolution_els = webdriver.find_elements_by_id('resolution')
            if resolution_els:
                dropdown_length = len(Select(resolution_els[0]).options)
                random_resolution_id = random.randint(1, dropdown_length - 1)
                Select(resolution_els[0]).select_by_index(random_resolution_id)

            def __filer_epic(element):
                return "epic" not in element.get_attribute("class").lower()

            webdriver.find_element_by_id(ISSUE_TYPE_DROPDOWN).click()
            issue_elements_in_dropdown = webdriver.find_elements_by_class_name("aui-list-item")
            if issue_elements_in_dropdown:
                filtered_issue_elements = list(filter(__filer_epic, issue_elements_in_dropdown))
                rnd_issue_type_el = random.choice(filtered_issue_elements)
                action = ActionChains(webdriver)
                action.move_to_element(rnd_issue_type_el).click(rnd_issue_type_el).perform()

            # Wait until issue-form saves issue-type
            _wait_until(webdriver, ec.invisibility_of_element_located((By.CSS_SELECTOR, ".buttons>.throbber")),
                        interaction)

            @print_timing
            def measure(webdriver, interaction):
                _wait_until(webdriver, ec.element_to_be_clickable((By.ID, "create-issue-submit")), interaction).click()
                _wait_until(webdriver, ec.invisibility_of_element_located((By.ID, "create-issue-dialog")), interaction)

            measure(webdriver, "selenium_create_issue:submit_issue_form")

        measure(webdriver, "selenium_create_issue:fill_and_submit_issue_form")

    measure(webdriver, "selenium_create_issue")
    _dismiss_popup(webdriver, '.aui-inline-dialog-contents .cancel')


def view_project_summary(webdriver, datasets):
    project_key = random.choice(datasets["issues"])[2]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/browse/{project_key}/summary')
        _wait_until(webdriver, ec.presence_of_element_located((By.CLASS_NAME, "project-meta-column")), interaction)

    measure(webdriver, "selenium_project_summary")



def search_jql(webdriver, datasets):
    jql = urllib.parse.quote(random.choice(datasets["jqls"][0]))

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(APPLICATION_URL + f"/issues/?jql={jql}")
        _wait_until(webdriver, AnyEc(
            ec.presence_of_element_located((By.ID, "issuetable")),
            ec.presence_of_element_located((By.ID, "issue-content")),
            ec.presence_of_element_located((By.CLASS_NAME, "no-results-hint"))
        ), interaction)

    measure(webdriver, "selenium_search_jql")


def edit_issue(webdriver, datasets):
    issue_id = random.choice(datasets["issues"])[1]

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            # open editor
            webdriver.get(f'{APPLICATION_URL}/secure/EditIssue!default.jspa?id={issue_id}')
            _wait_until(webdriver, ec.presence_of_element_located((By.ID, "issue-edit")), interaction)

        measure(webdriver, "selenium_edit_issue:open_edit_issue_form")

        # edit summary
        text_summary = f"Edit summary form selenium - {generate_random_string(10)}"
        webdriver.find_element_by_id('summary').send_keys(text_summary)

        # edit description
        text_description = f"Edit description form selenium - {generate_random_string(30)}"
        element = webdriver.find_element_by_id('description')
        _write_to_text_area(webdriver, element, text_description, interaction)

        @print_timing
        def measure(webdriver, interaction):
            webdriver.find_element_by_id('issue-edit-submit').click()
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "summary-val")), interaction)

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
        pages = len(datasets['project_keys']) // page_size
        webdriver.get(APPLICATION_URL +
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
