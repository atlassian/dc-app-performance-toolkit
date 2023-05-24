import random
import urllib.parse

from selenium_ui.conftest import print_timing
from util.api.jira_clients import JiraRestClient
from util.conf import JIRA_SETTINGS

from selenium_ui.jira.sfj_pages.SkillsetField import SkillsetField
from selenium_ui.jira.sfj_pages.ExpertFinder import ExpertFinder
from selenium_ui.jira.sfj_pages.Assignments import AssignmentsDashboard
from selenium_ui.jira.sfj_pages.Inspector import Inspector
from selenium_ui.jira.sfj_pages.RiskAnalysis import RiskAnalysis
from selenium_ui.jira.sfj_pages.Simulation import Simulation
from selenium_ui.jira.pages.pages import Issue

from selenium_ui.jira.pages.selectors import UrlManager, LoginPageLocators, LogoutLocators

client = JiraRestClient(JIRA_SETTINGS.server_url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password)
rte_status = client.check_rte_status()


def view_skillset(webdriver, datasets):
    page = SkillsetField(webdriver, issue_key=datasets['issue_key'], issue_id=datasets['issue_id'])

    edit_skillset(webdriver, datasets)
    @print_timing("selenium_view_skillset")
    def measure():
        page.view_skillset()

    measure()


def edit_skillset(webdriver, datasets):
    page = SkillsetField(webdriver, issue_key=datasets['issue_key'], issue_id=datasets['issue_id'])

    page.go_to_edit_issue()
    
    @print_timing("selenium_edit_skillset")
    def measure():
        page.edit_skillset()

    measure()


def open_expert_finder(webdriver, datasets):
    page = ExpertFinder(webdriver)
    
    @print_timing("selenium_open_expert_finder")
    def measure():
        page.open_expert_finder()

    measure()

def open_assignments_dashboard(webdriver, datasets):
    page = AssignmentsDashboard(webdriver)
    
    @print_timing("selenium_open_assignments_dashboard")
    def measure():
        page.open_assignments_dashboard()

    measure()
    
def pull_assignment(webdriver, datasets):
    page = AssignmentsDashboard(webdriver)
    
    open_assignments_dashboard(webdriver, datasets)

    @print_timing("selenium_pull_assignment")
    def measure():
        page.pull_assignment()

    measure()

def open_inspector(webdriver, datasets):
    page = Inspector(webdriver)
    
    @print_timing("selenium_open_inspector")
    def measure():
        page.open_inspector()

    measure()

def inspector_select_user(webdriver, datasets):
    page = Inspector(webdriver)

    open_inspector(webdriver, datasets)
    
    @print_timing("selenium_inspector_select_user")
    def measure():
        page.select_user()

    measure()


def open_risk_analysis(webdriver, datasets):
    page = RiskAnalysis(webdriver, project_key=datasets['project_key'])
    
    @print_timing("selenium_open_risk_analysis")
    def measure():
        page.open_risk_analysis()

    measure()

def run_risk_analysis(webdriver, datasets):
    page = RiskAnalysis(webdriver, project_key=datasets['project_key'])
    
    open_risk_analysis(webdriver, datasets)
    
    @print_timing("selenium_run_risk_analysis")
    def measure():
        page.run_risk_analysis()

    measure()

def open_simulation(webdriver, datasets):
    page = Simulation(webdriver)
    
    @print_timing("selenium_open_simulation")
    def measure():
        page.open_simulation()

    measure()

def run_simulation(webdriver, datasets):
    page = Simulation(webdriver)
    
    open_simulation(webdriver, datasets)
    
    @print_timing("selenium_run_simulation")
    def measure():
        page.run_simulation()

    measure()
