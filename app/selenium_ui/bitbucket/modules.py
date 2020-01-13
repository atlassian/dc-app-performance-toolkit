import random
import time
import urllib.parse

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from selenium_ui.conftest import print_timing, AnyEc, generate_random_string
from util.conf import BITBUCKET_SETTINGS

APPLICATION_URL = BITBUCKET_SETTINGS.server_url
DASHBOARD_URL = f"{BITBUCKET_SETTINGS.server_url}/dashboard"
PROJECTS_URL = f"{BITBUCKET_SETTINGS.server_url}/projects"
timeout = 10


def get_random_user(datasets):
    return random.choice(datasets["users"])


def get_random_project_repo(datasets):
    random_project = random.choice(datasets["projects"])
    project_key = random_project[0]
    project_repos = random_project[1:]
    repo_key = random.choice(project_repos)
    return [project_key, repo_key]


def login(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/login')

        measure(webdriver, "selenium_login:open_login_page")
        user = random.choice(datasets["users"])
        webdriver.find_element_by_id('j_username').send_keys(user[0])
        webdriver.find_element_by_id('j_password').send_keys(user[1])

        @print_timing
        def measure(webdriver, interaction):
            webdriver.find_element_by_id('submit').click()
            WebDriverWait(webdriver, timeout).until(
                lambda webdriver: webdriver.find_element(By.CLASS_NAME, "marketing-page-footer") or
                                  webdriver.find_element(By.CLASS_NAME, "dashboard-your-work"))

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
    project_key = get_random_project_repo(datasets)[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f"{PROJECTS_URL}/{project_key}")
        _wait_until(webdriver, ec.presence_of_element_located((By.ID, "repositories-container")), interaction)
    measure(webdriver, "selenium_view_project_repositories")


def view_repo(webdriver, datasets):
    random_project = get_random_project_repo(datasets)
    project_key = random_project[0]
    repo_key = random_project[1]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f"{PROJECTS_URL}/{project_key}/repos/{repo_key}/browse")
        _wait_until(webdriver, ec.presence_of_element_located((By.ID, "repo-clone-dialog")), interaction)
    measure(webdriver, "selenium_view_repository")


def view_pr_overview(webdriver, datasets):

    def get_pull_requests(webdriver):
        while not get_element_or_none(webdriver, By.CSS_SELECTOR, '#repository-nav-pull-requests>aui-badge'):
            random_project = get_random_project_repo(datasets)
            project_key = random_project[0]
            repo_key = random_project[1]
            webdriver.get(f"{PROJECTS_URL}/{project_key}/repos/{repo_key}/browse")
            if get_element_or_none(webdriver, By.CSS_SELECTOR, '#repository-nav-pull-requests>aui-badge'):
                break

    get_pull_requests(webdriver)

    @print_timing
    def measure(webdriver, interaction):
        webdriver.find_element(webdriver, By.CSS_SELECTOR, '#repository-nav-pull-requests>aui-badge').click()
        _wait_until(webdriver, ec.presence_of_element_located((By.ID, "pull-requests-content")), interaction)
    measure(webdriver, 'selenium_view_pull_requests')










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