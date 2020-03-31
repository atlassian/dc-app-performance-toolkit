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
            login_page.at()
            webdriver.app_version = login_page.get_app_version()
        measure(webdriver, "selenium_login:open_login_page")

        login_page.set_credentials(datasets['username'], datasets['password'])

        @print_timing
        def measure(webdriver, interaction):
            login_page.submit_login(interaction)
            get_started_page = GetStarted(webdriver)
            get_started_page.at()
            get_started_page.get_started_widget_visible(interaction)
        measure(webdriver, "selenium_login:login_get_started")
    measure(webdriver, "selenium_login")


def view_dashboard(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        dashboard = Dashboard(webdriver)
        dashboard.go_to()
        dashboard.at()
        dashboard.dashboard_presented(interaction)
    measure(webdriver, "selenium_view_dashboard")


def view_projects(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        projects = Projects(webdriver)
        projects.go_to()
        projects.at()
        projects.projects_list_presented(interaction)
    measure(webdriver, "selenium_view_projects")


def view_project_repos(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        project = Project(webdriver, project_key=datasets['project_key'])
        project.go_to()
        project.repositories_visible(interaction)
    measure(webdriver, "selenium_view_project_repositories")


def view_repo(webdriver, datasets):
    repository = Repository(webdriver,
                            project_key=datasets['project_key'],
                            repo_slug=datasets['repo_slug'])

    @print_timing
    def measure(webdriver, interaction):
        repository.go_to()
        repository.at()
        nav_panel = RepoNavigationPanel(webdriver)
        nav_panel.wait_navigation_panel_presented(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, "selenium_view_repository")


def view_list_pull_requests(webdriver, datasets):
    repo_pull_requests = RepoPullRequests(webdriver,
                                          project_key=datasets['project_key'],
                                          repo_slug=datasets['repo_slug'])

    @print_timing
    def measure(webdriver, interaction):
        repo_pull_requests.go_to()
        repo_pull_requests.at()
        repo_pull_requests.pull_requests_list_visible(interaction)
    measure(webdriver, 'selenium_view_list_pull_requests')


def view_pull_request_overview_tab(webdriver, datasets):
    pull_request = PullRequest(webdriver, project_key=datasets['project_key'],
                               repo_slug=datasets['repo_slug'],
                               pull_request_key=datasets['pull_request_id'])

    @print_timing
    def measure(webdriver, interaction):
        pull_request.go_to_overview()
        pull_request.at()
        pull_request.pull_request_tab_presented(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_pull_request_overview')


def view_pull_request_diff_tab(webdriver, datasets):
    pull_request = PullRequest(webdriver, project_key=datasets['project_key'],
                               repo_slug=datasets['repo_slug'],
                               pull_request_key=datasets['pull_request_id'])

    @print_timing
    def measure(webdriver, interaction):
        pull_request.go_to_diff()
        pull_request.wait_diff_tab_presented(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_pull_request_diff')


def view_pull_request_commits_tab(webdriver, datasets):
    pull_request = PullRequest(webdriver, project_key=datasets['project_key'],
                               repo_slug=datasets['repo_slug'],
                               pull_request_key=datasets['pull_request_id'])

    @print_timing
    def measure(webdriver, interaction):
        pull_request.go_to_commits()
        pull_request.wait_commit_msg_label(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_pull_request_commits')


def comment_pull_request_diff(webdriver, datasets):
    pull_request = PullRequest(webdriver, project_key=datasets['project_key'],
                               repo_slug=datasets['repo_slug'],
                               pull_request_key=datasets['pull_request_id'])
    pull_request.go_to_diff()
    @print_timing
    def measure(webdriver, interaction):
        PopupManager(webdriver).dismiss_default_popup()
        pull_request.wait_diff_tab_presented(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        pull_request.wait_code_diff_to_be_visible(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        pull_request.click_inline_comment_button_js()
        if webdriver.app_version == '6':
            pull_request.add_code_comment_v6(interaction)
        elif webdriver.app_version == '7':
            pull_request.add_code_comment_v7(interaction)
    measure(webdriver, 'selenium_comment_pull_request_file')


def comment_pull_request_overview(webdriver, datasets):
    pull_request = PullRequest(webdriver, project_key=datasets['project_key'],
                               repo_slug=datasets['repo_slug'],
                               pull_request_key=datasets['pull_request_id'])
    pull_request.go_to()
    pull_request.at()
    @print_timing
    def measure(webdriver, interaction):
        PopupManager(webdriver).dismiss_default_popup()
        pull_request.wait_pull_request_activity_visible(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        pull_request.wait_comment_text_area_visible(interaction).click()
        pull_request.add_overview_comment(interaction)
        pull_request.click_save_comment_button(interaction)
    measure(webdriver, 'selenium_comment_pull_request_overview')


def view_branches(webdriver, datasets):
    branches = RepositoryBranches(webdriver, project_key=datasets['project_key'],
                                  repo_slug=datasets['repo_slug'])

    @print_timing
    def measure(webdriver, interaction):
        branches.go_to()
        branches.wait_branch_name_visible(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_branches')


def create_pull_request(webdriver, datasets):
    repository = Repository(webdriver,
                            project_key=datasets['project_key'],
                            repo_slug=datasets['repo_slug'])
    repo_pull_requests = RepoPullRequests(webdriver, repo_slug=repository.repo_slug, project_key=repository.project_key)
    repository_branches = RepositoryBranches(webdriver, repo_slug=repository.repo_slug,
                                             project_key=repository.project_key)
    navigation_panel = RepoNavigationPanel(webdriver)
    PopupManager(webdriver).dismiss_default_popup()

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            branch_from = datasets['pull_request_branch_from']
            branch_to = datasets['pull_request_branch_to']
            repository_branches.open_base_branch(interaction=interaction,
                                                 base_branch_name=branch_from)
            fork_branch_from = repository_branches.create_branch_fork_rnd_name(interaction=interaction,
                                                                               base_branch_name=branch_from)
            navigation_panel.wait_navigation_panel_presented(interaction)
            repository_branches.open_base_branch(interaction=interaction,
                                                 base_branch_name=branch_to)
            fork_branch_to = repository_branches.create_branch_fork_rnd_name(interaction=interaction,
                                                                               base_branch_name=branch_to)
            datasets['pull_request_fork_branch_to'] = fork_branch_to
            navigation_panel.wait_navigation_panel_presented(interaction)

            repo_pull_requests.create_new_pull_request(interaction=interaction, from_branch=fork_branch_from,
                                                       to_branch=fork_branch_to)
            PopupManager(webdriver).dismiss_default_popup()

        measure(webdriver, 'selenium_create_pull_request:create_pull_request')

        @print_timing
        def measure(webdriver, interaction):
            PopupManager(webdriver).dismiss_default_popup()
            pull_request = PullRequest(webdriver)
            pull_request.wait_pull_request_activity_visible(interaction)
            PopupManager(webdriver).dismiss_default_popup()
            pull_request.merge_pull_request(interaction)
        measure(webdriver, 'selenium_create_pull_request:merge_pull_request')
        repository_branches.go_to()
        repository_branches.delete_branch(interaction=interaction,
                                          branch_name=datasets['pull_request_fork_branch_to'])
    measure(webdriver, 'selenium_create_pull_request')


def view_commits(webdriver, datasets):
    repo_commits = RepositoryCommits(webdriver, project_key=datasets['project_key'], repo_slug=datasets['repo_slug'])
    @print_timing
    def measure(webdriver, interaction):
        repo_commits.go_to()
        repo_commits.at()
        repo_commits.commit_graph_is_visible(interaction)
        PopupManager(webdriver).dismiss_default_popup()
    measure(webdriver, 'selenium_view_commits')


def logout(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        logout_page = LogoutPage(webdriver)
        logout_page.go_to()
    measure(webdriver, "selenium_log_out")
