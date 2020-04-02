import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from selenium_ui.conftest import AnyEc, generate_random_string, print_timing
from util.conf import CONFLUENCE_SETTINGS

from selenium_ui.confluence.pages.pages import Login, AllUpdates, PopupManager, Page, Dashboard, TopNavPanel, Editor

timeout = 20

# TODO consider do not use conftest as utility class and do not import it in modules
APPLICATION_URL = CONFLUENCE_SETTINGS.server_url


def setup_run_data(datasets):
    user = random.choice(datasets["users"])
    page = random.choice(datasets["pages"])
    blog = random.choice(datasets["blogs"])
    datasets['username'] = user[0]
    datasets['password'] = user[1]
    datasets['page_id'] = page[0]
    datasets['blog_id'] = blog[0]


def login(webdriver, datasets):
    setup_run_data(datasets)
    login_page = Login(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        @print_timing
        def measure(webdriver, interaction):
            login_page.go_to()
            login_page.wait_for_page_loaded(interaction)
        measure(webdriver, "selenium_login:open_login_page")

        login_page.set_credentials(username=datasets['username'], password=datasets['password'])

        @print_timing
        def measure(webdriver, interaction):
            login_page.click_login_button(interaction)
            if login_page.is_first_login():
                login_page.first_user_setup(interaction)
            all_updates_page = AllUpdates(webdriver)
            all_updates_page.wait_for_page_loaded(interaction)
        measure(webdriver, "selenium_login:login_and_view_dashboard")
    measure(webdriver, 'selenium_login')
    PopupManager(webdriver).dismiss_default_popup()


def view_page(webdriver, datasets):
    page = Page(webdriver, page_id=datasets['page_id'])

    @print_timing
    def measure(webdriver, interaction):
        page.go_to()
        page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_page")


def view_blog(webdriver, datasets):
    blog = Page(webdriver, page_id=datasets['blog_id'])

    @print_timing
    def measure(webdriver, interaction):
        blog.go_to()
        blog.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_blog")


def view_dashboard(webdriver, datasets):
    dashboard_page = Dashboard(webdriver)
    
    @print_timing
    def measure(webdriver, interaction):
        dashboard_page.go_to()
        dashboard_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_view_dashboard")


def create_page(webdriver, datasets):
    nav_panel = TopNavPanel(webdriver)
    edit_page = Editor(webdriver)
    @print_timing
    def measure(webdriver, interaction):
        nav_panel.click_create(interaction)
        PopupManager(webdriver).dismiss_default_popup()
        edit_page.wait_for_page_loaded(interaction)
    measure(webdriver, "selenium_create_page:open_create_page_editor")

    PopupManager(webdriver).dismiss_default_popup()

    edit_page.write_title()
    populate_page_content(webdriver)

    @print_timing
    def measure(webdriver, interaction):
        webdriver.find_element_by_id("rte-button-publish").click()
        _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'title-text')), interaction)

    measure(webdriver, "selenium_create_page:save_created_page")


def edit_page(webdriver, datasets):
    page = random.choice(datasets["pages"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/pages/editpage.action?pageId={page}')
        _wait_until(webdriver,
                    AnyEc(ec.text_to_be_present_in_element((By.CLASS_NAME, 'status-indicator-message'), 'Ready to go'),
                          ec.text_to_be_present_in_element((By.CLASS_NAME, 'status-indicator-message'), 'Changes saved')
                          ), interaction)

        _wait_until(webdriver, ec.element_to_be_clickable((By.ID, 'rte-button-publish')), interaction)

    measure(webdriver, "selenium_edit_page:open_create_page_editor")

    populate_page_content(webdriver)

    @print_timing
    def measure(webdriver, interaction):
        confirmation_button = "qed-publish-button"
        webdriver.find_element_by_id("rte-button-publish").click()
        if webdriver.find_elements_by_id(confirmation_button):
            if webdriver.find_element_by_id('qed-publish-button').is_displayed():
                webdriver.find_element_by_id('qed-publish-button').click()
        _wait_until(webdriver, ec.invisibility_of_element_located((By.ID, 'rte-spinner')), interaction)
        _wait_until(webdriver, AnyEc(ec.presence_of_element_located((By.ID, "title-text")),
                                     ec.presence_of_element_located((By.ID, confirmation_button))
                                     ), interaction)

    measure(webdriver, "selenium_edit_page:save_edited_page")


def create_comment(webdriver, datasets):
    view_page(webdriver, datasets)

    @print_timing
    def measure(webdriver, interaction):
        webdriver.execute_script("document.querySelector('.quick-comment-prompt').click()")
        _wait_until(webdriver, ec.frame_to_be_available_and_switch_to_it((By.ID, 'wysiwygTextarea_ifr')), interaction)
        webdriver.find_element_by_id("tinymce").find_element_by_tag_name('p')\
            .send_keys(f"This is page comment from date {time.time()}")
        webdriver.switch_to.parent_frame()

    measure(webdriver, 'selenium_create_comment:write_comment')

    @print_timing
    def measure(webdriver, interaction):
        webdriver.find_element_by_id("rte-button-publish").click()
        _wait_until(webdriver, ec.visibility_of_element_located((By.CSS_SELECTOR, '.quick-comment-prompt')),
                    interaction)

    measure(webdriver, "selenium_create_comment:save_comment")


def populate_page_title(webdriver):
    _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'content-title')), 'populate page title')
    title = "Selenium - " + generate_random_string(10)
    webdriver.find_element_by_id("content-title").clear()
    webdriver.find_element_by_id("content-title").send_keys(title)


def populate_page_content(webdriver):
    _wait_until(webdriver,
                ec.frame_to_be_available_and_switch_to_it((By.ID, 'wysiwygTextarea_ifr')), 'populate page content')
    webdriver.find_element_by_id("tinymce").find_element_by_tag_name('p').send_keys(generate_random_string(30))
    webdriver.switch_to.parent_frame()


def log_out(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/logout.action')

    measure(webdriver, "selenium_log_out")


def _wait_until(webdriver, expected_condition, interaction, time_out=timeout):
    message = f"Interaction: {interaction}. "
    ec_type = type(expected_condition)
    if ec_type == AnyEc:
        conditions_text = ""
        for ecs in expected_condition.ecs:
            conditions_text = conditions_text + " " + f"Condition: {str(ecs)} Locator: {ecs.locator}\n"

        message += f"Timed out after {time_out} sec waiting for one of the conditions: \n{conditions_text}"

    elif ec_type == ec.invisibility_of_element_located:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.target}")

    elif ec_type == ec.frame_to_be_available_and_switch_to_it:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.frame_locator}")

    else:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.locator}")

    return WebDriverWait(webdriver, time_out).until(expected_condition, message=message)
