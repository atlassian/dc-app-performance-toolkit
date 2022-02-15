from util.conf import JSM_SETTINGS
from selenium.webdriver.common.by import By


class PopupLocators:
    default_popup = '.aui-message .icon-close'
    popup_1 = 'form.tip-footer>.helptip-close'
    popup_2 = '.aui-inline-dialog-contents .cancel'
    popup_3 = '.dialog-close-button'
    popup_4 = '.aui-close-button'
    popup_5 = '.aui-button aui-button-link'
    popup_6 = '//button[contains(text(),"OK, got it")]'


class UrlManager:

    def __init__(self, project_key=None, request_key=None, queue_id=None, custom_report_id=None,
                 insight_issues_id=None, schema_id=None):
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
        self.view_issue_with_insight_object_params = f'/browse/{insight_issues_id}'
        self.view_insight_schema_params = f'/secure/ObjectSchema.jspa?id={schema_id}'
        # with correct dataset need to be replaced with right variable(random issue with object)

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

    def view_insight_schema(self):
        return f'{self.host}{self.view_insight_schema_params}'


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
    dashboard_params = UrlManager().dashboard_params
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


class ViewReportsLocators:
    # locators to click
    workload = (By.XPATH, "//span[contains(text(),'Workload')]")
    time_to_resolution = (By.XPATH, "//span[contains(text(),'Time to resolution')]")
    created_vs_resolved = (By.XPATH, "//span[contains(text(),'Created vs Resolved')]")

    # wait until visible locators
    reports_nav = (By.ID, "pinnednav-opts-sd-reports-nav")
    custom_report_content = (By.CSS_SELECTOR, "#sd-report-content .js-report-graph.sd-graph-container")
    team_workload_agents_table = (By.CSS_SELECTOR, ".js-page-panel-content.sd-page-panel-content .aui.sd-agents-table")


class ViewQueueLocators:
    queues = (By.CSS_SELECTOR, "#pinnednav-opts-sd-queues-nav li")
    queues_status = (By.XPATH, "//span[contains(text(),'Status')]")
    queue_is_empty = (By.CSS_SELECTOR, '.sd-queue-empty')


class InsightLocators:
    # insight_all_selectors
    # insight_schema
    insight_dropdown = (By.ID, "rlabs_insight_topmenu_link")
    insight_object_schemas_button = (By.ID, "rlabs_insight_manage_class_models_lnk")
    # insight_create_new_schema
    dialog_window_1 = (By.ID, "dialog-submit-button")
    dialog_window_3 = (By.XPATH, "//a[contains(text(),'No, thanks')]")
    create_object_schemas = (By.XPATH, "//a[contains(text(),'Create Object Schema')]")
    object_schemas_hr_schema = (By.CLASS_NAME, "rlabs-template-preview")
    dialog_window_2 = (By.XPATH, "//button[contains(text(),'OK, got it')]")
    object_schemas_next_button = (By.XPATH, "//button[contains(text(),'Next')]")
    object_schemas_name_field = (By.ID, "rlabs-insight-create-name")
    object_schemas_key_field = (By.ID, "rlabs-insight-create-key")
    object_schemas_create_button = (By.XPATH, "//button[contains(text(),'Create')]")
    # insight_create_new_object
    create_object_button = (By.XPATH, "//button[contains(text(),'Create Object')]")
    view_all_schemas_selector = (By.ID, "rlabs-manage-main")
    random_insight_schema = (By.XPATH, "//a[contains(text(),'test schema')]")
    object_name_field = (By.CSS_SELECTOR, "#rlabs-insight-attribute")
    create_button = (By.XPATH, "//body/div[@id='rlabs-insight-dialog']/div[1]/div[2]/button[1]")
    admin_menu_dropdown = (By.ID, "admin_menu")
    admin_menu_issue = (By.ID, "admin_issues_menu")
    custom_fields_settings = (By.XPATH, "//a[@id='view_custom_fields']")
    add_custom_field_button = (By.ID, "add_custom_fields")
    pop_up_after_create_object = (By.XPATH, "//body/div[@id='aui-flag-container']/div[1]/div[1]")

    # view_queue_insight_column
    view_queue_insight_column = (By.XPATH, "//span[contains(text(),'Insight')]")
    insight_column = (By.CLASS_NAME, "_3DjtzZ5cCJ")

    # search_insight_object_by_IQL
    search_object_by_iql = (By.ID, "rlabs_iam_search_lnk")
    search_object_text_field = (By.CSS_SELECTOR, "textarea[name='iql']")
    search_iql_button = (By.CLASS_NAME, "rIcon-search")

    # view_issue_with_object
    custom_field_insight = (By.ID, "rowForcustomfield_10600")
