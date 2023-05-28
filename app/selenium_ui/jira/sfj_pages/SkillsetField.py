from selenium.webdriver.common.by import By
from selenium_ui.jira.pages.pages import Issue

class SkillsetField(Issue):
    def __init__(self, driver, issue_key=None, issue_id=None):
        Issue.__init__(self, driver, issue_key, issue_id)

        self.selectors = {
            "skillset_view": ".skillset-root > .skillset-view",
            "skillset_view_skills": ".skillset-root > .skillset-view span",
            "skillset_edit": ".skillset-root > .skillset-edit",
            "skillset_edit_categories": ".skillset-root > .skillset-edit .category",
            "skillset_edit_skills": ".skillset-root > .skillset-edit .skill input",
            "skillset_edit_skills_checked": ".skillset-root > .skillset-edit .skill input:checked",
            "skillset_edit_skills_unchecked": ".skillset-root > .skillset-edit .skill input:not(:checked)",
            "skillset_edit_form_submit": ".save-options button[type=submit]",
        }
        
    def edit_issue_with_skillset(self):
        categories = self.get_elements((By.CSS_SELECTOR, self.selectors['skillset_edit_categories']))
        for i, category in enumerate(categories):
            if i < 3:
                self.wait_until_clickable(category).click()
            else:
                break;
        
        self.wait_until_visible((By.CSS_SELECTOR, self.selectors['skillset_edit_skills_unchecked']))
        skills = self.get_elements((By.CSS_SELECTOR, self.selectors['skillset_edit_skills_unchecked']))
        self.driver.execute_script(f"document.querySelector('{self.selectors['skillset_edit_skills_unchecked']}').checked = true")

        self.edit_issue_submit()
        self.wait_for_issue_title()

    def view_issue_with_skillset(self):
        self.go_to_url(self.page_url)
        self.wait_until_visible((By.CSS_SELECTOR, self.selectors['skillset_view_skills']))

    def edit_skillset(self):
        self.wait_until_visible((By.CSS_SELECTOR, self.selectors['skillset_view_skills']))
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['skillset_view_skills'])).click()
        self.wait_until_clickable((By.CSS_SELECTOR, self.selectors['skillset_edit_categories']))

        skills = self.get_elements((By.CSS_SELECTOR, self.selectors['skillset_edit_skills_unchecked']))
        for (i, skill) in enumerate(skills):
            if i < 2:
                self.wait_until_clickable(skill).click()
                
        self.get_element((By.CSS_SELECTOR, self.selectors['skillset_edit_form_submit'])).click()

        self.wait_until_visible((By.CSS_SELECTOR, self.selectors['skillset_view_skills']))