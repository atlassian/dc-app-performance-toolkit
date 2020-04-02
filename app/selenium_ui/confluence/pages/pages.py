
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
        elif self.get_element(LoginPageLocators.current_step_sel).text == 'Upload your photo':
            self.wait_until_clickable(LoginPageLocators.skip_photo_upload, interaction).click()
        elif self.get_element(LoginPageLocators.current_step_sel).text == 'Find content':
            self.wait_until_any_element_visible(LoginPageLocators.skip_find_content, interaction)[0].click()
            self.wait_until_clickable(LoginPageLocators.finish_setup, interaction).click()


class AllUpdates(BasePage):
    page_loaded_selector = AllUpdatesLocators.updates_content


class PopupManager(BasePage):

    def dismiss_default_popup(self):
        return self.dismiss_popup(PopupLocators.default_popup, PopupLocators.popup_1, PopupLocators.popup_2,
                                  PopupLocators.dialog_window)


class Page(BasePage):
    page_loaded_selector = PageLocators.page_title

    def __init__(self, driver, page_id):
        BasePage.__init__(self, driver)
        url_manager = UrlManager(page_id=page_id)
        self.page_url = url_manager.page_url()


class Dashboard(BasePage):
    page_url = DashboardLocators.dashboard_url
    page_loaded_selector = DashboardLocators.updated_items


class TopNavPanel(BasePage):

    def click_create(self, interaction):
        self.wait_until_clickable(TopPanelLocators.create_button, interaction).click()


class Editor(BasePage):
    page_loaded_selector = EditorLocators.publish_button

    def write_title(self):
        title_field = self.wait_until_visible(EditorLocators.title_field, interaction='page title')
        title = "Selenium - " + self.generate_random_string(10)
        title_field.clear()
        title_field.send_keys(title)

    def write_content(self):


