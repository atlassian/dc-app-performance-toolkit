import random

from selenium_ui.base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium_ui.jsd.pages.agent_selectors import LoginPageLocators, PopupLocators, DashboardLocators, LogoutLocators, \
    BrowseProjectsLocators, BrowseCustomersLocators, ViewCustomerRequestLocators, UrlManager, ViewReportsLocators, \
    ViewQueueLocators


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.default_popup, PopupLocators.popup_1, PopupLocators.popup_2)


class Login(BasePage):
    page_url = LoginPageLocators.login_url
    page_loaded_selector = LoginPageLocators.system_dashboard

    def is_first_login(self):
        return True if self.get_elements(LoginPageLocators.continue_button) else False

    def first_login_setup(self):
        self.wait_until_visible(LoginPageLocators.continue_button).send_keys(Keys.ESCAPE)
        self.get_element(LoginPageLocators.continue_button).click()
        self.wait_until_visible(LoginPageLocators.avatar_page_next_button).click()
        self.wait_until_visible(LoginPageLocators.explore_current_projects).click()
        self.go_to_url(DashboardLocators.dashboard_url)
        self.wait_until_visible(DashboardLocators.dashboard_window)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()


class Logout(BasePage):
    page_url = LogoutLocators.logout_url

    def click_logout(self):
        self.get_element(LogoutLocators.logout_submit_button).click()

    def wait_for_page_loaded(self):
        self.wait_until_present(LogoutLocators.login_button_link)


class BrowseProjects(BasePage):
    page_url = BrowseProjectsLocators.brows_projects_url

    def wait_for_page_loaded(self):
        self.wait_until_visible(BrowseProjectsLocators.page_title)


class BrowseCustomers(BasePage):

    def __init__(self, driver, project_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.browse_project_customers_page_url()

    def wait_for_page_loaded(self):
        self.wait_until_visible(BrowseCustomersLocators.page_title)


class ViewCustomerRequest(BasePage):

    def __init__(self, driver, request_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(request_key=request_key)
        self.page_url = url_manager.view_customer_request_url()

    def wait_for_page_loaded(self):
        self.wait_until_visible(ViewCustomerRequestLocators.bread_crumbs)

    def add_request_comment(self, rte_status):
        comment_text = f"Add comment from selenium - {self.generate_random_string(30)}"
        self.get_element(ViewCustomerRequestLocators.comment_collapsed_textarea).click()

        if rte_status:
            self.wait_until_available_to_switch(ViewCustomerRequestLocators.comment_text_field_RTE)
            self.action_chains().send_keys_to_element(
                self.get_element(ViewCustomerRequestLocators.comment_tinymce_field), comment_text).perform()
            self.return_to_parent_frame()
        else:
            self.get_element(ViewCustomerRequestLocators.comment_text_field).send_keys(comment_text)

        self.get_element(ViewCustomerRequestLocators.comment_internally_btn).click()
        self.wait_until_visible(ViewCustomerRequestLocators.comment_collapsed_textarea)


class ViewReports(BasePage):

    def __init__(self, driver, project_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.browse_project_reports_url()

    def wait_for_page_loaded(self):
        self.wait_until_visible(ViewReportsLocators.reports_nav)

    def view_time_to_resolution_report(self):
        self.get_element(ViewReportsLocators.time_to_resolution).click()
        self.wait_until_visible(ViewReportsLocators.custom_report_content)

    def view_workload_report(self):
        self.get_element(ViewReportsLocators.workload).click()
        self.wait_until_visible(ViewReportsLocators.team_workload_agents_table)

    def view_created_vs_resolved(self):
        self.get_element(ViewReportsLocators.created_vs_resolved).click()
        self.wait_until_visible(ViewReportsLocators.custom_report_content)


class ViewQueue(BasePage):

    def __init__(self, driver, project_key=None, queue_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, queue_id=queue_id)
        self.page_url = url_manager.view_queue_all_open()

    def wait_for_page_loaded(self):
        self.wait_until_clickable(ViewQueueLocators.reporter)

    def get_random_queue(self):
        queues = self.get_elements(ViewQueueLocators.queues)
        random_queue = random.choice([queue for queue in queues if queue.text.partition('\n')[0] != 'All open'
                                      and queue.text.partition('\n')[2] != '0'])
        random_queue.click()
        self.wait_until_clickable(ViewQueueLocators.reporter)
