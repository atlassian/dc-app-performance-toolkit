import random
from selenium_ui.conftest import print_timing

from selenium_ui.bitbucket.pages.pages import LoginPage, GetStarted, Dashboard, Projects, Project, Repository, \
    RepoNavigationPanel, PopupManager, RepoPullRequests, PullRequest, RepositoryBranches, RepositoryCommits, LogoutPage


def setup_run_data(datasets):
    user = random.choice(datasets["users"])
    project_with_repo_prs = random.choice(datasets["pull_requests"])
    datasets['username'] = user[1]
    datasets['password'] = user[2]
    datasets['project_key'] = project_with_repo_prs[1]
    datasets['repo_slug'] = project_with_repo_prs[0]
    datasets['pull_request_branch_from'] = project_with_repo_prs[3]
    datasets['pull_request_branch_to'] = project_with_repo_prs[4]
    datasets['pull_request_id'] = project_with_repo_prs[2]


def login(webdriver, datasets):
    setup_run_data(datasets)
    login_page = LoginPage(webdriver)

    @print_timing("selenium_login")
    def measure():

        @print_timing("selenium_login:open_login_page")
        def sub_measure():
            login_page.go_to()
            webdriver.app_version = login_page.get_app_major_version()
            if login_page.is_logged_in():
                login_page.delete_all_cookies()
                login_page.go_to()
        sub_measure()

        login_page.set_credentials(datasets['username'], datasets['password'])

        @print_timing("selenium_login:login_get_started")
        def sub_measure():
            login_page.submit_login()
            get_started_page = GetStarted(webdriver)
            get_started_page.wait_for_page_loaded()
            webdriver.node_id = login_page.get_node_id()
            print(f"node_id:{webdriver.node_id}")
        sub_measure()

    measure()


def view_dashboard(webdriver, datasets):

    @print_timing("selenium_view_dashboard")
    def measure():
        dashboard_page = Dashboard(webdriver)
        dashboard_page.go_to()
        dashboard_page.wait_for_page_loaded()
    measure()


def view_projects(webdriver, datasets):

    @print_timing("selenium_view_projects")
    def measure():
        projects_page = Projects(webdriver)
        projects_page.go_to()
        projects_page.wait_for_page_loaded()
    measure()


def view_project_repos(webdriver, datasets):

    @print_timing("selenium_view_project_repositories")
    def measure():
        project_page = Project(webdriver, project_key=datasets['project_key'])
        project_page.go_to()
        project_page.wait_for_page_loaded()
    measure()


def view_repo(webdriver, datasets):
    repository_page = Repository(webdriver,
                                 project_key=datasets['project_key'],
                                 repo_slug=datasets['repo_slug'])

    @print_timing("selenium_view_repository")
    def measure():
        repository_page.go_to()
        nav_panel = RepoNavigationPanel(webdriver)
        nav_panel.wait_for_page_loaded()
        PopupManager(webdriver).dismiss_default_popup()
    measure()


def view_list_pull_requests(webdriver, datasets):
    repo_pull_requests_page = RepoPullRequests(webdriver,
                                               project_key=datasets['project_key'],
                                               repo_slug=datasets['repo_slug'])

    @print_timing("selenium_view_list_pull_requests")
    def measure():
        repo_pull_requests_page.go_to()
        repo_pull_requests_page.wait_for_page_loaded()
    measure()


def view_pull_request_overview_tab(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])

    @print_timing("selenium_view_pull_request_overview")
    def measure():
        pull_request_page.go_to_overview()
        pull_request_page.wait_for_overview_tab()
        PopupManager(webdriver).dismiss_default_popup()
    measure()


def view_pull_request_diff_tab(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])

    @print_timing("selenium_view_pull_request_diff")
    def measure():
        pull_request_page.go_to_diff()
        pull_request_page.wait_for_diff_tab()
        PopupManager(webdriver).dismiss_default_popup()
    measure()


def view_pull_request_commits_tab(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])

    @print_timing("selenium_view_pull_request_commits")
    def measure():
        pull_request_page.go_to_commits()
        pull_request_page.wait_for_commits_tab()
        PopupManager(webdriver).dismiss_default_popup()
    measure()


def comment_pull_request_diff(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])
    pull_request_page.go_to_diff()

    @print_timing("selenium_comment_pull_request_file")
    def measure():
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.wait_for_diff_tab()
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.wait_for_code_diff()
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.click_inline_comment_button_js()
        pull_request_page.add_code_comment()
    measure()


def comment_pull_request_overview(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])
    pull_request_page.go_to()

    @print_timing("selenium_comment_pull_request_overview")
    def measure():
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.wait_for_overview_tab()
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.add_overview_comment()
        pull_request_page.click_save_comment_button()
    measure()


def view_branches(webdriver, datasets):
    branches_page = RepositoryBranches(webdriver, project_key=datasets['project_key'],
                                       repo_slug=datasets['repo_slug'])

    @print_timing("selenium_view_branches")
    def measure():
        branches_page.go_to()
        branches_page.wait_for_page_loaded()
        PopupManager(webdriver).dismiss_default_popup()
    measure()


def create_pull_request(webdriver, datasets):
    repository_page = Repository(webdriver,
                                 project_key=datasets['project_key'],
                                 repo_slug=datasets['repo_slug'])
    repo_pull_requests_page = RepoPullRequests(webdriver, repo_slug=repository_page.repo_slug,
                                               project_key=repository_page.project_key)
    repository_branches_page = RepositoryBranches(webdriver, repo_slug=repository_page.repo_slug,
                                                  project_key=repository_page.project_key)
    navigation_panel = RepoNavigationPanel(webdriver)
    PopupManager(webdriver).dismiss_default_popup()

    @print_timing("selenium_create_pull_request")
    def measure():

        @print_timing("selenium_create_pull_request:create_pull_request")
        def sub_measure():
            branch_from = datasets['pull_request_branch_from']
            branch_to = datasets['pull_request_branch_to']
            repository_branches_page.open_base_branch(base_branch_name=branch_from)
            fork_branch_from = repository_branches_page.create_branch_fork_rnd_name(base_branch_name=branch_from)
            navigation_panel.wait_for_navigation_panel()
            repository_branches_page.open_base_branch(base_branch_name=branch_to)
            fork_branch_to = repository_branches_page.create_branch_fork_rnd_name(base_branch_name=branch_to)
            datasets['pull_request_fork_branch_to'] = fork_branch_to
            navigation_panel.wait_for_navigation_panel()
            repo_pull_requests_page.create_new_pull_request(from_branch=fork_branch_from, to_branch=fork_branch_to)
            PopupManager(webdriver).dismiss_default_popup()
        sub_measure()

        @print_timing("selenium_create_pull_request:merge_pull_request")
        def sub_measure():
            PopupManager(webdriver).dismiss_default_popup()
            pull_request_page = PullRequest(webdriver)
            pull_request_page.wait_for_overview_tab()
            PopupManager(webdriver).dismiss_default_popup()
            pull_request_page.merge_pull_request()
        sub_measure()

        repository_branches_page.go_to()
        repository_branches_page.wait_for_page_loaded()
        repository_branches_page.delete_branch(branch_name=datasets['pull_request_fork_branch_to'])
    measure()


def view_commits(webdriver, datasets):
    repo_commits_page = RepositoryCommits(webdriver, project_key=datasets['project_key'],
                                          repo_slug=datasets['repo_slug'])

    @print_timing("selenium_view_commits")
    def measure():
        repo_commits_page.go_to()
        repo_commits_page.wait_for_page_loaded()
        PopupManager(webdriver).dismiss_default_popup()
    measure()


def logout(webdriver, datasets):

    @print_timing("selenium_log_out")
    def measure():
        logout_page_page = LogoutPage(webdriver)
        logout_page_page.go_to()
    measure()
