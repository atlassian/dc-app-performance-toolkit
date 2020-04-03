
from selenium_ui.base_page import BasePage

from selenium_ui.confluence.pages.selectors import UrlManager, LoginPageLocators, AllUpdatesLocators, PopupLocators,\
    PageLocators, DashboardLocators, TopPanelLocators, EditorLocators


class Login(BasePage):
    page_url = LoginPageLocators.login_page_url
    page_loaded_selector = LoginPageLocators.login_button

    def set_credentials(self, username, password):
        self.get_element(LoginPageLocators.login_username_field).send_keys(username)
        self.get_element(LoginPageLocators.login_password_field).send_keys(password)

    def click_login_button(self, interaction):
        self.wait_until_visible(LoginPageLocators.login_button, interaction).click()
        self.wait_until_invisible(LoginPageLocators.login_button, interaction)

    def is_first_login(self):
        elems = self.get_elements(LoginPageLocators.first_login_setup_page)
        return True if elems else False

    def first_user_setup(self, interaction):
        if self.get_element(LoginPageLocators.current_step_sel).text == 'Welcome':
            self.wait_until_clickable(LoginPageLocators.skip_welcome_button, interaction).click()
        if self.get_element(LoginPageLocators.current_step_sel).text == 'Upload your photo':
            self.wait_until_clickable(LoginPageLocators.skip_photo_upload, interaction).click()
        if self.get_element(LoginPageLocators.current_step_sel).text == 'Find content':
            self.wait_until_any_element_visible(LoginPageLocators.skip_find_content, interaction)[0].click()
            self.wait_until_clickable(LoginPageLocators.finish_setup, interaction).click()


class Logout(BasePage):
    page_url = UrlManager().logout_url()


class AllUpdates(BasePage):
    page_loaded_selector = AllUpdatesLocators.updates_content


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.timezone_popups, PopupLocators.skip_onbording_1,
                                  PopupLocators.skip_onboarding_2,
                                  PopupLocators.time_saving_template)


class Page(BasePage):
    page_loaded_selector = PageLocators.page_title

    def __init__(self, driver, page_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(page_id=page_id)
        self.page_url = url_manager.page_url()

    def click_add_comment(self):
        css_selector = PageLocators.comment_text_field[1]
        self.execute_js(f"document.querySelector('{css_selector}').click()")

    def wait_for_comment_field(self, interaction):
        self.wait_until_visible(PageLocators.comment_text_field, interaction)


class Dashboard(BasePage):
    page_url = DashboardLocators.dashboard_url
    page_loaded_selector = DashboardLocators.updated_items


class TopNavPanel(BasePage):

    def click_create(self, interaction):
        self.wait_until_clickable(TopPanelLocators.create_button, interaction).click()


class Editor(BasePage):

    def __init__(self, driver, page_id=None):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(page_id=page_id)
        self.page_url = url_manager.edit_page_url()

    def wait_for_create_page_open(self, interaction):
        self.wait_until_clickable(EditorLocators.publish_button, interaction)

    def wait_for_page_loaded(self, interaction):
        self.wait_for_editor_open(interaction)
        self.wait_until_clickable(EditorLocators.publish_button, interaction)

    def write_title(self):
        title_field = self.wait_until_visible(EditorLocators.title_field, interaction='page title')
        title = "Selenium - " + self.generate_random_string(10)
        title_field.clear()
        title_field.send_keys(title)

    def write_content(self, interaction, text=None):
        self.wait_until_available_to_switch(EditorLocators.page_content_field, interaction=interaction)
        text = self.generate_random_string(30) if not text else text
        tinymce_text_el = self.get_element(EditorLocators.tinymce_page_content_field)
        tinymce_text_el.find_element_by_tag_name('p').send_keys(text)
        self.return_to_parent_frame()

    def click_submit(self):
        self.get_element(EditorLocators.publish_button).click()

    def wait_for_editor_open(self, interaction):
        self.wait_until_any_ec_text_presented_in_el(selector_names=[(EditorLocators.status_indicator, 'Ready to go'),
                                                                    (EditorLocators.status_indicator, 'Changes saved')],
                                                    interaction=interaction)

    def save_edited_page(self, interaction):
        self.get_element(EditorLocators.publish_button).click()
        if self.get_elements(EditorLocators.confirm_publishing_button):
            if self.get_element(EditorLocators.confirm_publishing_button).is_displayed():
                self.get_element(EditorLocators.confirm_publishing_button).click()
        self.wait_until_invisible(EditorLocators.save_spinner, interaction)
        self.wait_until_any_ec_presented(selector_names=[PageLocators.page_title,
                                                         EditorLocators.confirm_publishing_button],
                                         interaction=interaction)
