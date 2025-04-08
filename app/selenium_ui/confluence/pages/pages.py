import time

from selenium_ui.base_page import BasePage

from selenium_ui.confluence.pages.selectors import UrlManager, LoginPageLocators, AllUpdatesLocators, PopupLocators,\
    PageLocators, DashboardLocators, TopPanelLocators, EditorLocators, LogoutLocators, XsrfTokenLocators, AdminLocators


class Login(BasePage):
    page_url = LoginPageLocators.login_page_url
    page_loaded_selector = [LoginPageLocators.login_button, LoginPageLocators.login_button_2sv]

    def __init__(self, driver):
        super().__init__(driver)
        self.is_2sv_login = False

    def wait_for_page_loaded(self):
        self.wait_until_visible(LoginPageLocators.sidebar)
        if not self.get_elements(LoginPageLocators.login_button):
            self.is_2sv_login = True
            print("INFO: 2sv login form")

    def set_credentials(self, username, password):
        if self.is_2sv_login:
            username_field = LoginPageLocators.login_username_field_2sv
            password_field = LoginPageLocators.login_password_field_2sv
        else:
            username_field = LoginPageLocators.login_username_field
            password_field = LoginPageLocators.login_password_field

        self.get_element(username_field).send_keys(username)
        self.get_element(password_field).send_keys(password)

    def click_login_button(self):
        if self.is_2sv_login:
            self.wait_until_visible(LoginPageLocators.login_button_2sv).click()
        else:
            self.wait_until_visible(LoginPageLocators.login_button).click()

    def is_first_login(self):
        elements = self.get_elements(LoginPageLocators.first_login_setup_page)
        return True if elements else False

    def is_logged_in(self):
        elements = self.get_elements(LoginPageLocators.logout)
        return True if elements else False

    def first_user_setup(self):
        if self.get_element(LoginPageLocators.current_step_sel).text == 'Welcome':
            self.wait_until_clickable(LoginPageLocators.skip_welcome_button).click()
        if self.get_element(LoginPageLocators.current_step_sel).text == 'Upload your photo':
            self.wait_until_clickable(LoginPageLocators.skip_photo_upload).click()
        if self.get_element(LoginPageLocators.current_step_sel).text == 'Find content':
            self.wait_until_any_element_visible(LoginPageLocators.skip_find_content)[0].click()
            self.wait_until_clickable(LoginPageLocators.finish_setup).click()

    def get_app_version(self):
        text = self.get_element(LoginPageLocators.footer_build_info).text
        return text

    def get_node_id(self):
        if self.get_elements(LoginPageLocators.footer_node_info):
            text = self.get_element(LoginPageLocators.footer_node_info).text
            return text.split(':')[-1].replace(')', '').replace(' ', '')
        else:
            return "SERVER"


class Logout(BasePage):
    page_url = UrlManager().logout_url()

    def wait_for_logout(self):
        self.wait_until_visible(LoginPageLocators.sidebar)


class AllUpdates(BasePage):
    page_loaded_selector = AllUpdatesLocators.updates_content


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.popup_selectors)


class Page(BasePage):
    page_loaded_selector = PageLocators.page_title

    def __init__(self, driver, page_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(page_id=page_id)
        self.page_url = url_manager.page_url()

    def wait_for_page_loaded(self):
        self.wait_until_visible(self.page_loaded_selector)
        self.wait_for_js_statement(key='document.readyState', value='complete',
                                   exception_msg=f"Page {self.page_url} could not be loaded. Please check the UI.")

    def click_add_comment(self):
        css_selector = PageLocators.comment_text_field[1]
        self.execute_js(f"document.querySelector('{css_selector}').click()")

    def wait_for_comment_field(self):
        self.wait_until_visible(PageLocators.comment_text_field)

    def click_edit(self):
        self.wait_until_clickable(PageLocators.edit_page_button).click()

    def wait_for_resources_loaded(self, timeout=5):
        start_time = time.time()
        print(f'Waiting for resources to be loaded: {timeout} s.')
        while time.time() - start_time < timeout:
            loaded = self.execute_js("return require('confluence-editor-loader/editor-loader').resourcesLoaded();")
            if loaded:
                print(f'Resources are loaded after {time.time() - start_time} s.')
                break
        else:
            print(f'WARNING: confluence-editor-loader resources were not loaded in {timeout} s')


class Dashboard(BasePage):
    page_url = DashboardLocators.dashboard_url
    page_loaded_selector = DashboardLocators.all_updates


class TopNavPanel(BasePage):

    def click_create(self):
        self.wait_until_clickable(TopPanelLocators.create_button).click()


class Editor(BasePage):

    def __init__(self, driver, page_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(page_id=page_id)

        xsrf_token = self.get_element(XsrfTokenLocators.xsrf_token).get_attribute('content')
        self.page_url = url_manager.edit_page_url() + "&atl_token=" + xsrf_token

    def wait_for_create_page_open(self):
        self.wait_until_clickable(EditorLocators.publish_button)

    def wait_for_page_loaded(self):
        self.wait_for_editor_open()
        self.wait_until_clickable(EditorLocators.publish_button)

    def write_title(self):
        title_field = self.wait_until_visible(EditorLocators.title_field)
        title = "Selenium - " + self.generate_random_string(10)
        title_field.clear()
        title_field.send_keys(title)

    def write_content(self, text=None):
        self.wait_until_available_to_switch(EditorLocators.page_content_field)
        text = self.generate_random_string(30) if not text else text
        self.execute_js(f"tinymce=document.getElementById('tinymce'); "
                        f"tag_p = document.createElement('p'); "
                        f"tag_p.textContent += '{text}'; "
                        f"tinymce.appendChild(tag_p)")
        self.return_to_parent_frame()

    def click_submit(self):
        self.get_element(EditorLocators.publish_button).click()

    def wait_for_editor_open(self):
        self.wait_until_any_ec_text_presented_in_el(
            selector_text_list=[(EditorLocators.status_indicator, 'Ready to go'),
                                (EditorLocators.status_indicator, 'Changes saved')])

    def save_edited_page(self):
        self.get_element(EditorLocators.publish_button).click()
        if self.get_elements(EditorLocators.confirm_publishing_button):
            if self.get_element(EditorLocators.confirm_publishing_button).is_displayed():
                self.get_element(EditorLocators.confirm_publishing_button).click()
        self.wait_until_invisible(EditorLocators.save_spinner)
        self.wait_until_any_ec_presented(selectors=[PageLocators.page_title,
                                                    EditorLocators.confirm_publishing_button])


class AdminPage(BasePage):
    page_url = AdminLocators.admin_system_page_url
    page_loaded_selector = AdminLocators.login_form

    def is_websudo(self):
        return True if self.get_elements(AdminLocators.web_sudo_password) else False

    def do_websudo(self, password):
        self.wait_until_clickable(AdminLocators.web_sudo_password).send_keys(password)
        self.wait_until_clickable(AdminLocators.web_sudo_submit_btn).click()
        self.wait_until_visible(AdminLocators.edit_baseurl)

    def go_to(self, password=None):
        super().go_to()
        self.wait_for_page_loaded()
        if self.is_websudo():
            self.do_websudo(password)
