from util.conf import JSM_SETTINGS
from selenium.webdriver.common.by import By


class PopupLocators:
    default_popup = '.aui-message .icon-close'
    popup_1 = 'form.tip-footer>.helptip-close'
    popup_2 = '.aui-inline-dialog-contents .cancel'
    popup_3 = '.aui-close-button'
    popup_4 = '.aui-button aui-button-link'
    popup_5 = '.buttons-container > div > a'


class UrlManager:

    def __init__(self, project_key=None, request_key=None, queue_id=None, custom_report_id=None,
                 insight_issues=None, schema_id=None):
        self.host = JSM_SETTINGS.server_url
        self.login_params = '/login.jsp'
        self.logout_params = '/logoutconfirm.jsp'
        self.dashboard_params = '/secure/Dashboard.jspa'
        self.browse_all_projects = '/secure/BrowseProjects.jspa?selectedProjectType=service_desk'
        self.browse_project_customers = f'/projects/{project_key}/customers'
        self.view_customer_request = f'/browse/{request_key}'
        self.view_queue = f'/projects/{project_key}/queues/custom'
        self.queue_all_open = f'{self.view_queue}/{queue_id}'
        self.workload_report_params = f'/projects/{project_key}/reports/workload'
        self.custom_report_params = f'/projects/{project_key}/reports/custom/{custom_report_id}'
        self.view_insight_queue_params = f'{self.view_queue}/1102'
        self.view_issue_with_insight_object_params = f'/browse/{insight_issues}'
        self.view_insight_all_schemas_params = '/secure/ManageObjectSchema.jspa'
        self.insight_search_by_iql_params = f'/secure/insight/search?schema={schema_id}'

    def login_url(self):
        return f'{self.host}{self.login_params}'

    def dashboard_url(self):
        return f"{self.host}{self.dashboard_params}"

    def logout_url(self):
        return f"{self.host}{self.logout_params}"

    def browse_all_projects_url(self):
        return f'{self.host}{self.browse_all_projects}'

    def browse_project_customers_page_url(self):
        return f"{self.host}{self.browse_project_customers}"

    def view_customer_request_url(self):
        return f'{self.host}{self.view_customer_request}'

    def workload_report_url(self):
        return f'{self.host}{self.workload_report_params}'

    def custom_report_url(self):
        return f'{self.host}{self.custom_report_params}'

    def view_queue_all_open(self):
        return f'{self.host}{self.queue_all_open}'

    def view_insight_queue(self):
        return f'{self.host}{self.view_insight_queue_params}'

    def view_issue_with_object(self):
        return f'{self.host}{self.view_issue_with_insight_object_params}'

    def view_insight_all_schemas(self):
        return f'{self.host}{self.view_insight_all_schemas_params}'

    def insight_search_by_iql(self):
        return f'{self.host}{self.insight_search_by_iql_params}'


class LoginPageLocators:
    login_url = UrlManager().login_url()

    # First time login setup page
    continue_button = (By.ID, 'next')
    avatar_page_next_button = (By.CSS_SELECTOR, "input[value='Next']")
    explore_current_projects = (By.CSS_SELECTOR, "a[data-step-key='browseprojects']")
    login_field = (By.ID, 'login-form-username')
    password_field = (By.ID, 'login-form-password')
    login_submit_button = (By.ID, 'login-form-submit')
    system_dashboard = (By.ID, "dashboard")
    footer = (By.ID, 'footer-build-information')


class DashboardLocators:
    dashboard_url = UrlManager().dashboard_url()
    dashboard_window = (By.CLASS_NAME, "page-type-dashboard")


class LogoutLocators:
    logout_url = UrlManager().logout_url()
    logout_submit_button = (By.ID, "confirm-logout-submit")
    login_button_link = (By.CLASS_NAME, "login-link")


class BrowseProjectsLocators:
    brows_projects_url = UrlManager().browse_all_projects_url()
    page_title = (By.XPATH, "//h1[contains(text(),'Browse projects')]")


class BrowseCustomersLocators:
    page_title = (By.XPATH, "//h2[contains(text(),'Customers')]")


class ViewCustomerRequestLocators:
    bread_crumbs = (By.CSS_SELECTOR, ".aui-nav.aui-nav-breadcrumbs")

    comment_collapsed_textarea = (By.ID, "sd-comment-collapsed-textarea")
    comment_text_field_RTE = (By.XPATH, "//div[textarea[@id='comment']]//iframe")
    comment_text_field = (By.XPATH, "//textarea[@id='comment']")
    comment_tinymce_field = (By.ID, "tinymce")
    comment_internally_btn = (By.XPATH, "//button[contains(text(),'Comment internally')]")
    customers_sidebar_selector = (By.CSS_SELECTOR, 'span.aui-icon.aui-icon-large.sd-sidebar-icon.icon-sidebar-customers')


class ViewReportsLocators:
    custom_report_content = (By.CSS_SELECTOR, "#sd-report-content .js-report-graph.sd-graph-container")
    team_workload_agents_table = (By.CSS_SELECTOR, ".js-page-panel-content.sd-page-panel-content .aui.sd-agents-table")


class ViewQueueLocators:
    queues_status = (By.XPATH, "//span[contains(text(),'Status')]")
    queue_is_empty = (By.CSS_SELECTOR, '.sd-queue-empty')


class InsightNewSchemaLocators:
    submit_dialog_window = (By.CSS_SELECTOR, '#dialog-submit-button')
    create_object_schemas = (By.XPATH, "//a[contains(text(),'Create Object Schema')]")
    new_object_schema = (By.XPATH, "//div[contains(text(),'Create Sample IT Asset Schema')]")
    object_schemas_next_button = (By.XPATH, "//button[contains(text(),'Next')]")
    object_schemas_name_field = (By.CSS_SELECTOR, "#rlabs-insight-create-name")
    object_schemas_key_field = (By.CSS_SELECTOR, "#rlabs-insight-create-key")
    object_schemas_create_button = (By.XPATH, "//button[contains(text(),'Create')]")

    @staticmethod
    def get_new_object_schema_name_locator(name):
        return By.XPATH, f"//a[contains(text(),'{name}')]"


class InsightDeleteSchemaLocators:
    delete_window_selector = (By.CSS_SELECTOR, "#rlabs-insight-dialog > div")
    submit_delete_button = (By.CSS_SELECTOR, "#rlabs-insight-dialog > div > div.dialog-button-panel > button")
    schema_list = (By.ID, "rlabs-manage-main")

    @staticmethod
    def new_object_schema_id_locator(schema_id):
        return By.CSS_SELECTOR, f"a[aria-owns='rlabs-actions-{schema_id}"

    @staticmethod
    def new_object_schema_delete_button_locator(name):
        return By.ID, f"object-schema-delete-{name}"


class InsightNewObjectLocators:
    create_object_button = (By.ID, "rlabs-create-object")
    object_name_field = (By.CSS_SELECTOR, "input[id^=rlabs-insight-attribute-]")
    create_button = (By.XPATH, "//body/div[@id='rlabs-insight-dialog']/div[1]/div[2]/button[1]")
    pop_up_after_create_object = (By.XPATH, "//body/div[@id='aui-flag-container']/div[1]/div[1]")


class InsightViewQueueLocators:
    view_queue_page = (By.XPATH, "//section[@id='sd-page-panel']")
    view_queue_insight_column = (By.XPATH, "//span[contains(text(),'Insight')]")


class InsightSearchObjectIql:
    search_object_text_field = (By.CSS_SELECTOR, "textarea[name='iql']")
    search_iql_button = (By.CLASS_NAME, "rIcon-search")
    search_iql_success = (By.XPATH, "//thead/tr[1]")


class InsightViewIssue:
    issue_title = (By.ID, "summary-val")
    custom_field_insight = (By.CSS_SELECTOR, '[title="Insight"]')
