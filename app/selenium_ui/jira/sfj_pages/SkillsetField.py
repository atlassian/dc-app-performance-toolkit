from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_ui.conftest import retry
import time
import random
import json

from selenium_ui.conftest import print_timing
from selenium_ui.jira.pages.pages import Issue


class SkillsetField(Issue):
    def __init__(self, driver, issue_key=None, issue_id=None):
        Issue.__init__(self, driver, issue_key, issue_id)

        self.selectors = {
            "skillset_view": (By.CSS_SELECTOR, ".skillset-root > .skillset-view"),
            "skillset_view_skills": (By.CSS_SELECTOR, ".skillset-root > .skillset-view span"),
            "skillset_edit": (By.CSS_SELECTOR, ".skillset-root > .skillset-edit"),
            "skillset_edit_categories": (By.CSS_SELECTOR, ".skillset-root > .skillset-edit .category"),
            "skillset_edit_skills": (By.CSS_SELECTOR, ".skillset-root > .skillset-edit .skill")
        }

    def view_skillset(self):
        self.wait_until_visible(self.selectors['skillset_view_skills'])

    def edit_skillset(self):
        self.wait_until_clickable(self.selectors['skillset_edit_categories'])

        categories = self.get_elements(self.selectors['skillset_edit_categories'])
        for category in categories:
            category.click()
            
        skills = self.get_elements(self.selectors['skillset_edit_skills'])
        for skill in skills:
            skill.click()

        self.edit_issue_submit()
        self.wait_for_issue_title()
