import random
from selenium_ui.conftest import print_timing

from selenium_ui.bitbucket.pages.pages import LoginPage, GetStarted, Dashboard, Projects, Project, Repository, \
    RepoNavigationPanel, PopupManager, RepoPullRequests, PullRequest, RepositoryBranches, ForkRepositorySettings, \
    UserSettings, RepositoryCommits, LogoutPage


def setup_run_data(datasets):
    user = random.choice(datasets["users"])
    datasets['username'] = user[1]
    datasets['password'] = user[2]
    datasets['user_id'] = int(user[0]) - 1
    project_with_repo_prs = random.choice(datasets["pull_requests"])
    datasets['project_key'] = project_with_repo_prs[1]
    datasets['repo_slug'] = project_with_repo_prs[0]
    # If PRs number > 2, choose random between first 2 PRs
    datasets['pull_request_id'] = random.choice([project_with_repo_prs[2], project_with_repo_prs[5]
                                                if len(project_with_repo_prs) > 5 else project_with_repo_prs[2]])
    datasets['pull_request_branch_from'] = project_with_repo_prs[3]
    datasets['pull_request_branch_to'] = project_with_repo_prs[4]


def login(webdriver, datasets):
    setup_run_data(datasets)
    login_page = LoginPage(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            login_page.go_to()
            webdriver.app_version = login_page.get_app_version()
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
        pull_request.click_save_comment_button(interaction)
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
    navigation_panel = RepoNavigationPanel(webdriver)
    repository.go_to()
    PopupManager(webdriver).dismiss_default_popup()

    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            navigation_panel.wait_navigation_panel_presented(interaction)
            navigation_panel.fork_repo(interaction).click()
            repository.set_enable_fork_sync(interaction, value=False)
            fork_repo_name = repository.set_fork_repo_name()
            datasets['fork_repo_name'] = fork_repo_name
            repository.submit_fork_repo()
            navigation_panel.wait_navigation_panel_presented(interaction)
        measure(webdriver, 'selenium_create_pull_request:create_repos_fork')

        @print_timing
        def measure(webdriver, interaction):
            navigation_panel.create_pull_request(interaction)
            repo_pull_requests.create_new_pull_request(interaction)
            # Choose branch source
            repo_pull_requests.set_pull_request_source_branch(interaction,
                                                              source_branch=datasets['pull_request_branch_from'])
            # Choose destination repo
            repo_pull_requests.set_pull_request_destination_repo(interaction)
            # Choose branch destination
            dest_branch = datasets['pull_request_branch_to']
            repo_pull_requests.set_pull_request_destination_branch(interaction,
                                                                   destination_branch=dest_branch)
            # Submit pull request
            repo_pull_requests.submit_pull_request(interaction)
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

        @print_timing
        def measure(webdriver, interaction):
            repo_settings = ForkRepositorySettings(webdriver,
                                                   user=datasets['username'], repo_slug=datasets['fork_repo_name'])

            repo_settings.go_to()
            repo_settings.delete_repository(interaction, repo_slug=datasets['fork_repo_name'])
            user_settings = UserSettings(webdriver, user=datasets['username'])
            user_settings.at()
            user_settings.user_role_visible(interaction)
        measure(webdriver, 'selenium_create_pull_request:delete_fork_repo')
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
