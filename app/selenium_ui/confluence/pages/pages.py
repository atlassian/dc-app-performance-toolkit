from selenium_ui.base_page import BasePage

from selenium_ui.confluence.pages.selectors import UrlManager, LoginPageLocators, AllUpdatesLocators, PopupLocators,\
    PageLocators, DashboardLocators, TopPanelLocators, EditorLocators, LogoutLocators


class Login(BasePage):
    page_url = LoginPageLocators.login_page_url
    page_loaded_selector = LoginPageLocators.login_button

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_username_field).send_keys(username)
        self.get_element(LoginPageLocators.login_password_field).send_keys(password)

    def click_login_button(self):
        self.wait_until_visible(LoginPageLocators.login_button).click()
        self.wait_until_invisible(LoginPageLocators.login_button)

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
        self.wait_until_visible(LogoutLocators.logout_msg)


class AllUpdates(BasePage):
    page_loaded_selector = AllUpdatesLocators.updates_content


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.timezone_popups, PopupLocators.skip_onbording_1,
                                  PopupLocators.skip_onboarding_2,
                                  PopupLocators.time_saving_template,
                                  PopupLocators.welcome_to_confluence)


class Page(BasePage):
    page_loaded_selector = PageLocators.page_title

    def __init__(self, driver, page_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(page_id=page_id)
        self.page_url = url_manager.page_url()

    def click_add_comment(self):
        css_selector = PageLocators.comment_text_field[1]
        self.execute_js(f"document.querySelector('{css_selector}').click()")

    def wait_for_comment_field(self):
        self.wait_until_visible(PageLocators.comment_text_field)


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
        self.page_url = url_manager.edit_page_url()

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
