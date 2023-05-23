import random
import urllib.parse

from selenium_ui.conftest import print_timing
from util.api.jira_clients import JiraRestClient
from util.conf import JIRA_SETTINGS

from selenium_ui.jira.sfj_pages.SkillsetField import SkillsetField
from selenium_ui.jira.pages.pages import Issue

client = JiraRestClient(JIRA_SETTINGS.server_url, JIRA_SETTINGS.admin_login, JIRA_SETTINGS.admin_password)
rte_status = client.check_rte_status()

def view_skillset(webdriver, datasets):
    page = SkillsetField(webdriver, issue_key=datasets['issue_key'], issue_id=datasets['issue_id'])

    @print_timing("selenium_view_skillset")
    def measure():
        page.go_to()
        page.view_skillset();
        page.wait_for_page_loaded()

    measure()

def edit_skillset(webdriver, datasets):
    page = SkillsetField(webdriver, issue_key=datasets['issue_key'], issue_id=datasets['issue_id'])
    
    @print_timing("selenium_edit_skillset")
        
    def measure():
        page.go_to();
        page.edit_skillset();
        page.wait_for_page_loaded()
        
    measure()
