import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from selenium_ui.conftest import print_timing, AnyEc, generate_random_string
from util.conf import BITBUCKET_SETTINGS

APPLICATION_URL = BITBUCKET_SETTINGS.server_url
LOGIN_URL = f"{BITBUCKET_SETTINGS.server_url}/getting-started"
DASHBOARD_URL = f"{BITBUCKET_SETTINGS.server_url}/dashboard"
PROJECTS_URL = f"{BITBUCKET_SETTINGS.server_url}/projects"
timeout = 10


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
        def measure(webdriver, interaction):
            webdriver.get(f'{LOGIN_URL}')

        measure(webdriver, "selenium_login:open_login_page")
        user = random.choice(datasets["users"])
        datasets['current_user_id'] = int(user[0]) - 1
        webdriver.find_element_by_id('j_username').send_keys(user[1])
        webdriver.find_element_by_id('j_password').send_keys(user[2])

        @print_timing
        def measure(webdriver, interaction):
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "submit")),
                        interaction).click()
            _wait_until(webdriver, ec.presence_of_element_located((By.CLASS_NAME, "marketing-page-footer")), interaction)
        measure(webdriver, "selenium_login:login_get_started")

    measure(webdriver, "selenium_login")


def view_dashboard(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
       webdriver.get(DASHBOARD_URL)
       _wait_until(webdriver, ec.presence_of_element_located((By.CLASS_NAME, "dashboard-your-work")), interaction)
    measure(webdriver, "selenium_view_dashboard")


def view_projects(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
       webdriver.get(PROJECTS_URL)
       _wait_until(webdriver, ec.presence_of_element_located((By.ID, "projects-container")), interaction)
    measure(webdriver, "selenium_view_projects")


def view_project_repos(webdriver, datasets):
    project = random.choice(datasets["projects"])
    project_key = project[0]

    datasets['current_project_key'] = project_key
    project_url = f"{PROJECTS_URL}/{project_key}"
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f"{project_url}")
        _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "repositories-container")), interaction)
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, "span.repository-name")), interaction)

    measure(webdriver, "selenium_view_project_repositories")


def view_repo(webdriver, datasets):
    repos = webdriver.find_elements_by_css_selector('span.repository-name')
    repo = random.choice(repos)

    @print_timing
    def measure(webdriver, interaction):
        repo.click()
        _wait_until(webdriver, ec.presence_of_element_located((By.ID, "repo-clone-dialog")), interaction)
        _dismiss_popup(webdriver, '.feature-discovery-close')
    measure(webdriver, "selenium_view_repository")


def view_list_pull_requests(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        pr_button = '#repository-nav-pull-requests>aui-badge'
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, pr_button)), interaction).click()
        _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "pull-requests-content")), interaction)
    measure(webdriver, 'selenium_view_list_pull_requests')


def view_pull_request_overview_tab(webdriver, datasets):
    pull_requests = webdriver.find_elements_by_css_selector('a.pull-request-title')
    random_pr = random.choice(pull_requests)

    @print_timing
    def measure(webdriver, interaction):
        random_pr.click()
        _wait_until(webdriver, ec.visibility_of_any_elements_located((By.CSS_SELECTOR, "ul.tabs-menu")), interaction)
        _dismiss_popup(webdriver, '.feature-discovery-close')
    measure(webdriver, 'selenium_view_pull_request_overview')


def view_pull_request_diff_tab(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, "ul.tabs-menu>li:nth-child(2)>a")),
                    interaction).click()
        diff_tab = ".diff-tree-toolbar"
        _wait_until(webdriver, ec.visibility_of_any_elements_located((By.CSS_SELECTOR, diff_tab)), interaction)
        _dismiss_popup(webdriver, '.feature-discovery-close')
    measure(webdriver, 'selenium_view_pull_request_diff')


def view_pull_request_commits_tab(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        pr_commits = 'ul.tabs-menu>li:nth-child(3)>a'
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, pr_commits)), interaction).click()
        _wait_until(webdriver, ec.visibility_of_any_elements_located((By.CSS_SELECTOR, "tr>th.message")), interaction)
        _dismiss_popup(webdriver, '.feature-discovery-close')
    measure(webdriver, 'selenium_view_pull_request_commits')


def comment_pull_request_diff(webdriver, datasets):
    webdriver.find_element_by_css_selector('ul.tabs-menu>li:nth-child(2)>a').click()

    @print_timing
    def measure(webdriver, interaction):
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, ".diff-tree-toolbar")),
                    interaction)
        _wait_until(webdriver, ec.visibility_of_element_located((By.CLASS_NAME, "CodeMirror-code")),
                    interaction)
        diff_lines = webdriver.find_elements_by_css_selector('button.add-comment-trigger>span.aui-iconfont-add-comment')
        random_diff_line = random.choice(diff_lines)
        webdriver.execute_script('arguments[0].scrollIntoView(true);', random_diff_line)
        random_diff_line.click()
        comment_text_area = webdriver.find_element_by_css_selector('textarea.text')
        comment_text_area.send_keys(f"{generate_random_string(50)}")
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, "div.buttons>button:nth-child(1)")),
                    interaction).click()
    measure(webdriver, 'selenium_comment_pull_request_file')


def comment_pull_request_overview(webdriver, datasets):
    webdriver.find_element_by_css_selector('ul.tabs-menu>li:nth-child(1)>a').click()

    @print_timing
    def measure(webdriver, interaction):
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, ".pull-request-activity-content")),
                    interaction)
        _dismiss_popup(webdriver, 'button.aui-button-link.feature-discovery-close')
        comment_text_area = webdriver.find_element_by_css_selector('textarea.text')
        comment_text_area.click()
        comment_text_area.send_keys(f"{generate_random_string(50)}")
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, "div.buttons>button:nth-child(1)")),
                    interaction).click()
    measure(webdriver, 'selenium_comment_pull_request_overview')


def view_branches(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.find_element_by_css_selector('.aui-sidebar-group.sidebar-navigation>ul>li:nth-child(3)').click()
        _wait_until(webdriver, ec.visibility_of_any_elements_located((By.ID, "branch-name-column")), interaction)
        _dismiss_popup(webdriver, '.feature-discovery-close')
    measure(webdriver, 'selenium_view_branches')


def view_commits(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        commits = '.aui-sidebar-group.sidebar-navigation>ul>li:nth-child(2)'
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, commits)),
                    interaction).click()
        _wait_until(webdriver, ec.visibility_of_any_elements_located((By.CSS_SELECTOR, "svg.commit-graph")),
                    interaction)
        _dismiss_popup(webdriver, '.feature-discovery-close')
    measure(webdriver, 'selenium_view_commits')


def logout(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/j_atl_security_logout')
    measure(webdriver, "selenium_log_out")


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


def get_element_or_none(webdriver, by, element):
    try:
        element = webdriver.find_element(by, element)
        return element
    except NoSuchElementException:
        return None