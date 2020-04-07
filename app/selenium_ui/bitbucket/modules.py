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
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            login_page.go_to()
            webdriver.app_version = login_page.get_app_version()
        measure(webdriver, "selenium_login:open_login_page")

        login_page.set_credentials(datasets['username'], datasets['password'])

        @print_timing
        def measure(webdriver, interaction):
            login_page.submit_login(interaction)
            get_started_page = GetStarted(webdriver)
            get_started_page.wait_for_page_loaded(interaction)
        measure(webdriver, "selenium_login:login_get_started")
    measure(webdriver, "selenium_login")


def view_dashboard(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        dashboard_page = Dashboard(webdriver)
        dashboard_page.go_to()
        dashboard_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_dashboard")


def view_projects(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        projects_page = Projects(webdriver)
        projects_page.go_to()
        projects_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_projects")


def view_project_repos(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        project_page = Project(webdriver, project_key=datasets['project_key'])
        project_page.go_to()
        project_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_project_repositories")


def view_repo(webdriver, datasets):
    repository_page = Repository(webdriver,
                                 project_key=datasets['project_key'],
                                 repo_slug=datasets['repo_slug'])

    @print_timing
    def measure(webdriver, interaction):
        repository_page.go_to()
        nav_panel = RepoNavigationPanel(webdriver)
        nav_panel.wait_for_page_loaded(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, "selenium_view_repository")


def view_list_pull_requests(webdriver, datasets):
    repo_pull_requests_page = RepoPullRequests(webdriver,
                                               project_key=datasets['project_key'],
                                               repo_slug=datasets['repo_slug'])

    @print_timing
    def measure(webdriver, interaction):
        repo_pull_requests_page.go_to()
        repo_pull_requests_page.wait_for_page_loaded(interaction)
    measure(webdriver, 'selenium_view_list_pull_requests')


def view_pull_request_overview_tab(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])

    @print_timing
    def measure(webdriver, interaction):
        pull_request_page.go_to_overview()
        pull_request_page.wait_for_overview_tab(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_pull_request_overview')


def view_pull_request_diff_tab(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])

    @print_timing
    def measure(webdriver, interaction):
        pull_request_page.go_to_diff()
        pull_request_page.wait_for_diff_tab(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_pull_request_diff')


def view_pull_request_commits_tab(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])

    @print_timing
    def measure(webdriver, interaction):
        pull_request_page.go_to_commits()
        pull_request_page.wait_for_commits_tab(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_pull_request_commits')


def comment_pull_request_diff(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])
    pull_request_page.go_to_diff()
    @print_timing
    def measure(webdriver, interaction):
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.wait_for_diff_tab(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.wait_for_code_diff(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.click_inline_comment_button_js()
        pull_request_page.add_code_comment(interaction)
    measure(webdriver, 'selenium_comment_pull_request_file')


def comment_pull_request_overview(webdriver, datasets):
    pull_request_page = PullRequest(webdriver, project_key=datasets['project_key'],
                                    repo_slug=datasets['repo_slug'],
                                    pull_request_key=datasets['pull_request_id'])
    pull_request_page.go_to()
    @print_timing
    def measure(webdriver, interaction):
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.wait_for_overview_tab(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        pull_request_page.add_overview_comment(interaction)
        pull_request_page.click_save_comment_button(interaction)
    measure(webdriver, 'selenium_comment_pull_request_overview')


def view_branches(webdriver, datasets):
    branches_page = RepositoryBranches(webdriver, project_key=datasets['project_key'],
                                       repo_slug=datasets['repo_slug'])

    @print_timing
    def measure(webdriver, interaction):
        branches_page.go_to()
        branches_page.wait_for_page_loaded(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_branches')


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

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            branch_from = datasets['pull_request_branch_from']
            branch_to = datasets['pull_request_branch_to']
            repository_branches_page.open_base_branch(interaction=interaction,
                                                      base_branch_name=branch_from)
            fork_branch_from = repository_branches_page.create_branch_fork_rnd_name(interaction=interaction,
                                                                                    base_branch_name=branch_from)
            navigation_panel.wait_for_navigation_panel(interaction)
            repository_branches_page.open_base_branch(interaction=interaction,
                                                      base_branch_name=branch_to)
            fork_branch_to = repository_branches_page.create_branch_fork_rnd_name(interaction=interaction,
                                                                                  base_branch_name=branch_to)
            datasets['pull_request_fork_branch_to'] = fork_branch_to
            navigation_panel.wait_for_navigation_panel(interaction)

            repo_pull_requests_page.create_new_pull_request(interaction=interaction, from_branch=fork_branch_from,
                                                            to_branch=fork_branch_to)
            PopupManager(webdriver).dismiss_default_popup()

        measure(webdriver, 'selenium_create_pull_request:create_pull_request')

        @print_timing
        def measure(webdriver, interaction):
            PopupManager(webdriver).dismiss_default_popup()
            pull_request_page = PullRequest(webdriver)
            pull_request_page.wait_for_overview_tab(interaction)
            PopupManager(webdriver).dismiss_default_popup()
            pull_request_page.merge_pull_request(interaction)
        measure(webdriver, 'selenium_create_pull_request:merge_pull_request')
        repository_branches_page.go_to()
        repository_branches_page.wait_for_page_loaded(interaction)
        repository_branches_page.delete_branch(interaction=interaction,
                                               branch_name=datasets['pull_request_fork_branch_to'])
    measure(webdriver, 'selenium_create_pull_request')


def view_commits(webdriver, datasets):
    repo_commits_page = RepositoryCommits(webdriver, project_key=datasets['project_key'],
                                          repo_slug=datasets['repo_slug'])
    @print_timing
    def measure(webdriver, interaction):
        repo_commits_page.go_to()
        repo_commits_page.wait_for_page_loaded(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_commits')


def logout(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        logout_page_page = LogoutPage(webdriver)
        logout_page_page.go_to()
    measure(webdriver, "selenium_log_out")
