import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from selenium_ui.conftest import AnyEc, generate_random_string, print_timing
from util.conf import CONFLUENCE_SETTINGS

timeout = 20

# TODO consider do not use conftest as utility class and do not import it in modules
APPLICATION_URL = CONFLUENCE_SETTINGS.server_url


def _dismiss_popup(webdriver, *args):
    for elem in args:
        try:
            webdriver.execute_script(f"document.querySelector(\'{elem}\').click()")
        except:
            pass


def login(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):

        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/login.action')
            _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'loginButton')), interaction)

        measure(webdriver, "selenium_login:open_login_page")

        user = random.choice(datasets["users"])
        webdriver.find_element_by_id('os_username').send_keys(user[0])
        webdriver.find_element_by_id('os_password').send_keys(user[1])

        def _setup_page_is_presented():
            elems = webdriver.find_elements_by_id('grow-ic-nav-container')
            return True if elems else False

        def _user_setup():
            current_step_sel = 'grow-aui-progress-tracker-step-current'
            if webdriver.find_element_by_class_name(current_step_sel).text == 'Welcome':
                _wait_until(webdriver,
                            ec.element_to_be_clickable((By.ID, 'grow-intro-video-skip-button')),
                            interaction).click()
            if webdriver.find_element_by_class_name(current_step_sel).text == 'Upload your photo':
                _wait_until(webdriver,
                            ec.element_to_be_clickable((By.CSS_SELECTOR, '.aui-button-link')),
                            interaction).click()
            if webdriver.find_element_by_class_name(current_step_sel).text == 'Find content':
                _wait_until(webdriver,
                            ec.visibility_of_any_elements_located(
                                (By.CSS_SELECTOR, '.intro-find-spaces-space>.space-checkbox')),
                            interaction)[0].click()
                _wait_until(webdriver,
                            ec.element_to_be_clickable((By.CSS_SELECTOR, '.intro-find-spaces-button-continue')),
                            interaction).click()

        @print_timing
        def measure(webdriver, interaction):
            webdriver.find_element_by_id('loginButton').click()
            _wait_until(webdriver, ec.invisibility_of_element_located((By.ID, 'loginButton')), interaction)
            if _setup_page_is_presented():
                _user_setup()
            _wait_until(webdriver, ec.presence_of_element_located((By.CLASS_NAME, 'list-container-all-updates')),
                        interaction)

        measure(webdriver, "selenium_login:login_and_view_dashboard")  # waits for all updates

    measure(webdriver, 'selenium_login')

    _dismiss_popup(webdriver,
                   ".button-panel-button .set-timezone-button",
                   ".aui-button aui-button-link .skip-onboarding")


def view_page(webdriver, datasets):
    page = random.choice(datasets["pages"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/pages/viewpage.action?pageId={page}')
        _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'title-text')), interaction)

    measure(webdriver, "selenium_view_page")


def view_blog(webdriver, datasets):
    blog = random.choice(datasets["blogs"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/pages/viewpage.action?pageId={blog}')
        _wait_until(webdriver, ec.visibility_of_element_located((By.ID, 'title-text')), interaction)

    measure(webdriver, "selenium_view_blog")


def view_dashboard(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/dashboard.action#all-updates')
        _wait_until(webdriver, ec.visibility_of_element_located((By.CLASS_NAME, 'update-items')), interaction)

    measure(webdriver, "selenium_view_dashboard")


def create_page(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        _wait_until(webdriver, ec.element_to_be_clickable((By.ID, 'quick-create-page-button')), interaction).click()
        _dismiss_popup(webdriver, "#closeDisDialog")
        _wait_until(webdriver, ec.element_to_be_clickable((By.ID, 'rte-button-publish')), interaction)

    measure(webdriver, "selenium_create_page:open_create_page_editor")
    _dismiss_popup(webdriver, "#closeDisDialog")
    populate_page_title(webdriver)
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
