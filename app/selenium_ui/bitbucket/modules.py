import random

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from selenium_ui.conftest import print_timing, AnyEc, generate_random_string
from util.conf import BITBUCKET_SETTINGS

APPLICATION_URL = BITBUCKET_SETTINGS.server_url
LOGIN_URL = f"{BITBUCKET_SETTINGS.server_url}/getting-started"
DASHBOARD_URL = f"{BITBUCKET_SETTINGS.server_url}/dashboard"
PROJECTS_URL = f"{BITBUCKET_SETTINGS.server_url}/projects"
timeout = 20


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
        datasets['current_user_name'] = user[1]
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


def create_pull_request(webdriver, datasets):
    random_repo_with_pr = get_random_repo_with_pr(datasets)
    fork_name = f"fork-{random_repo_with_pr[0]}"
    webdriver.get(f"{PROJECTS_URL}/{random_repo_with_pr[1]}/repos/{random_repo_with_pr[0]}")
    _dismiss_popup(webdriver, '.feature-discovery-close')

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            _wait_until(webdriver, ec.presence_of_element_located((By.ID, "repo-clone-dialog")), interaction)
            safe_click(webdriver, By.CSS_SELECTOR, 'span.icon-fork', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, "enable-ref-syncing")),
                        interaction)
            safe_click(webdriver, By.ID, 'enable-ref-syncing', interaction)
            fork_name = f"fork-{random_repo_with_pr[0]}"
            fork_name_field = webdriver.find_element_by_id('name')
            fork_name_field.clear()
            fork_name_field.send_keys(f'{fork_name}')
            safe_click(webdriver, By.ID, "fork-repo-submit", interaction)
            _wait_until(webdriver, ec.presence_of_element_located((By.ID, "repo-clone-dialog")), interaction)
        measure(webdriver, 'selenium_create_pull_request:create_repos_fork')

        @print_timing
        def measure(webdriver, interaction):
            safe_click(webdriver, By.CSS_SELECTOR, '.aui-sidebar-group.sidebar-navigation>ul>li:nth-child(4)', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'pull-requests-content')), interaction)
            safe_click(webdriver, By.ID, 'empty-list-create-pr-button', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'branch-compare')), interaction)
            # Choose branch source
            safe_click(webdriver, By.ID, 'sourceBranch', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, 'ul.results-list')), interaction)
            branch_name_from_dropdown = webdriver.find_element_by_id('sourceBranchDialog-search-input')
            branch_name_from_dropdown.send_keys(f'{random_repo_with_pr[2]}')
            _wait_until(webdriver, ec.invisibility_of_element_located((By.CSS_SELECTOR,
                        '#sourceBranchDialog>div.results>div.spinner-wrapper')), interaction)
            branch_name_from_dropdown.send_keys(Keys.ENTER)
            _wait_until(webdriver, ec.invisibility_of_element_located((By.CSS_SELECTOR, 'ul.results-list')), interaction)
            # Choose project source
            safe_click(webdriver, By.ID, 'targetRepo', interaction)
            safe_click(webdriver, By.CSS_SELECTOR, "div#targetRepoDialog>div>ul.results-list>li:nth-child(1)",
                       interaction)
            # Choose branch destination
            _wait_until(webdriver, ec.visibility_of_element_located((
                        By.ID, 'targetBranch')), interaction)
            webdriver.execute_script("document.querySelector('#targetBranch').click()")
            #safe_click(webdriver, By.ID, 'targetBranch', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'targetBranchDialog')), interaction)
            branch_name_to_dropdown = webdriver.find_element_by_id('targetBranchDialog-search-input')
            branch_name_to_dropdown.send_keys(f'{random_repo_with_pr[3]}')
            _wait_until(webdriver, ec.invisibility_of_element_located(
                (By.CSS_SELECTOR, '#targetBranchDialog>div.results>div.spinner-wrapper')), interaction)
            branch_name_to_dropdown.send_keys(Keys.ENTER)
            _wait_until(webdriver, ec.invisibility_of_element_located((By.CSS_SELECTOR, 'ul.results-list')), interaction)
            _wait_until(webdriver, ec.element_to_be_clickable((By.ID, 'show-create-pr-button')),
                        interaction)
            safe_click(webdriver, By.ID, 'show-create-pr-button', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, 'textarea#pull-request-description')),
                        interaction)
            webdriver.find_element_by_id('title').clear()
            webdriver.find_element_by_id('title').send_keys('Selenium test pull request')
            safe_click(webdriver, By.ID, 'submit-form', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, 'div.activity-item-content')),
                        interaction)
            _wait_until(webdriver, ec.element_to_be_clickable((By.CSS_SELECTOR, 'button.merge-button')),
                        interaction)
            _dismiss_popup(webdriver, 'button.aui-button-link.feature-discovery-close')
        measure(webdriver, 'selenium_create_pull_request:create_pull_request')

        @print_timing
        def measure(webdriver, interaction):
            _dismiss_popup(webdriver, 'button.aui-button-link.feature-discovery-close')
            _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, 'div.activity-item-content')),
                        interaction)
            _dismiss_popup(webdriver, 'button.aui-button-link.feature-discovery-close')
            _wait_until(webdriver, ec.element_to_be_clickable((By.CSS_SELECTOR, 'button.merge-button')),
                        interaction)
            _dismiss_popup(webdriver, 'button.aui-button-link.feature-discovery-close')
            while not get_element_or_none(webdriver, By.CSS_SELECTOR, 'div.diagram-image'):
                webdriver.execute_script("document.querySelector('button.merge-button').click()")
            _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, 'div.diagram-image')),
                        interaction)
            safe_click(webdriver, By.CSS_SELECTOR, 'button.confirm-button', interaction)
            _wait_until(webdriver, ec.invisibility_of_element_located((By.CSS_SELECTOR,
                        'span.pull-request-cleanup-checkbox-wrapper')), interaction)
        measure(webdriver, 'selenium_create_pull_request:merge_pull_request')

        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f"{APPLICATION_URL}/users/{datasets['current_user_name']}/repos/{fork_name}/settings")
            _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR,
                        'div.aui-page-panel-nav')), interaction)
            safe_click(webdriver, By.ID, 'repository-settings-delete-button', interaction)
            webdriver.find_element_by_id('confirmRepoName').send_keys(f'{fork_name}')
            _wait_until(webdriver, ec.element_to_be_clickable((By.ID,
                                                               'delete-repository-dialog-submit')), interaction)
            safe_click(webdriver, By.ID, 'delete-repository-dialog-submit', interaction)
            _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR,
                                                                     'div.user-detail.username')), interaction)
        measure(webdriver, 'selenium_create_pull_request:delete_fork_repo')
    measure(webdriver, 'selenium_create_pull_request')


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


def safe_click(webdriver, by, element, interaction):
    return _wait_until(webdriver, ec.visibility_of_element_located((by, element)),
                       interaction).click()


def get_random_repo_with_pr(datasets):
    repos_with_prs = []
    prs = datasets['pull_requests']
    for pr in prs:
        # pr = [repo_slug, project_key, from_branch1, to_branch1, from_branch2, to_branch2...]
        if len(pr) >= 4:
            repos_with_prs.append(pr)
    if len(repos_with_prs) == 0:
        raise NoPullRequestFoundException('app/dataset/bitbucket/repos.csv does not have any pull request')
    return random.choice(repos_with_prs)



def get_element_or_none(webdriver, by, element):
    try:
        element = webdriver.find_element(by, element)
        return element
    except NoSuchElementException:
        return None


class NoPullRequestFoundException(Exception):
    pass