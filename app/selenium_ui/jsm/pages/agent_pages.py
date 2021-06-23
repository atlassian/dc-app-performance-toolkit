import random

from selenium_ui.base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium_ui.jsm.pages.agent_selectors import LoginPageLocators, PopupLocators, DashboardLocators, LogoutLocators, \
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

    def is_first_login_second_page(self):
        return True if self.get_elements(LoginPageLocators.avatar_page_next_button) else False

    def first_login_setup(self):
        self.wait_until_visible(LoginPageLocators.continue_button).send_keys(Keys.ESCAPE)
        self.get_element(LoginPageLocators.continue_button).click()
        self.first_login_second_page_setup()

    def first_login_second_page_setup(self):
        self.wait_until_visible(LoginPageLocators.avatar_page_next_button).click()
        self.wait_until_visible(LoginPageLocators.explore_current_projects).click()
        self.go_to_url(DashboardLocators.dashboard_url)
        self.wait_until_visible(DashboardLocators.dashboard_window)

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_field).send_keys(username)
        self.get_element(LoginPageLocators.password_field).send_keys(password)
        self.get_element(LoginPageLocators.login_submit_button).click()

    def __get_footer_text(self):
        return self.get_element(LoginPageLocators.footer).text

    def get_app_version(self):
        text = self.__get_footer_text()
        return text.split('#')[0].replace('(v', '')

    def get_node_id(self):
        text = self.__get_footer_text()
        return text.split(':')[-1].replace(')', '')


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
    timeout = 30

    def __init__(self, driver, request_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(request_key=request_key)
        self.page_url = url_manager.view_customer_request_url()

    def wait_for_page_loaded(self):
        self.wait_until_visible(ViewCustomerRequestLocators.bread_crumbs)

    def add_request_comment(self, rte_status):
        comment_text = f"Add comment from selenium - {self.generate_random_string(30)}"
        textarea = self.get_element(ViewCustomerRequestLocators.comment_collapsed_textarea)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
        textarea.click()

        if rte_status:
            self.wait_until_available_to_switch(ViewCustomerRequestLocators.comment_text_field_RTE)
            tinymce_field = self.get_element(ViewCustomerRequestLocators.comment_tinymce_field)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tinymce_field)
            self.action_chains().send_keys_to_element(tinymce_field, comment_text).perform()
            self.return_to_parent_frame()
        else:
            comment_text_field = self.get_element(ViewCustomerRequestLocators.comment_text_field)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", comment_text_field)
            self.action_chains().move_to_element(comment_text_field).click()\
                .send_keys_to_element(comment_text_field, comment_text).perform()

        comment_button = self.get_element(ViewCustomerRequestLocators.comment_internally_btn)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", comment_button)
        comment_button.click()
        self.wait_until_visible(ViewCustomerRequestLocators.comment_collapsed_textarea)


class Report:

    @staticmethod
    def view_workload_report(driver, project_key):
        return WorkloadReport(driver, project_key)

    @staticmethod
    def view_time_to_resolution_report(driver, project_key, time_to_resolution_report_id):
        return TimeToResolutionReport(driver, project_key, time_to_resolution_report_id)

    @staticmethod
    def view_created_vs_resolved_report(driver, project_key, created_vs_resolved_report_id):
        return CreatedResolvedReport(driver, project_key, created_vs_resolved_report_id)


class WorkloadReport(BasePage):
    page_loaded_selector = ViewReportsLocators.team_workload_agents_table
    timeout = 60

    def __init__(self, driver, project_key=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key)
        self.page_url = url_manager.workload_report_url()


class TimeToResolutionReport(BasePage):
    page_loaded_selector = ViewReportsLocators.custom_report_content
    timeout = 60

    def __init__(self, driver, project_key, time_to_resolution_report_id):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, custom_report_id=time_to_resolution_report_id)
        self.page_url = url_manager.custom_report_url()


class CreatedResolvedReport(BasePage):
    page_loaded_selector = ViewReportsLocators.custom_report_content
    timeout = 60

    def __init__(self, driver, project_key, time_to_resolution_report_id):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, custom_report_id=time_to_resolution_report_id)
        self.page_url = url_manager.custom_report_url()


class ViewQueue(BasePage):
    timeout = 60

    def __init__(self, driver, project_key=None, queue_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(project_key=project_key, queue_id=queue_id)
        self.page_url = url_manager.view_queue_all_open()

    def wait_for_page_loaded(self):
        self.wait_until_visible(ViewQueueLocators.queues_status)

    def get_random_queue(self):
        queues = self.get_elements(ViewQueueLocators.queues)
        random_queue = random.choice([queue for queue in queues
                                      if queue.text.partition('\n')[0] not in
                                      ['All open', 'Recently resolved', 'Resolved past 7 days']
                                      and queue.text.partition('\n')[2] != '0'])
        random_queue.click()
        self.wait_until_visible(ViewQueueLocators.queues_status, timeout=self.timeout)
