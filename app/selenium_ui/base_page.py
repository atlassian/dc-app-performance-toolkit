from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium_ui.conftest import AnyEc
import random
import string

TIMEOUT = 20


class BasePage:
    page_url = ''
    page_loaded_selector = {}

    def __init__(self, driver):
        self.driver = driver

    def go_to(self):
        self.driver.get(self.page_url)

    def wait_for_page_loaded(self, interaction):
        if type(self.page_loaded_selector) == list:
            for selector in self.page_loaded_selector:
                self.wait_until_visible(selector, interaction)
        else:
            self.wait_until_visible(self.page_loaded_selector, interaction)

    def go_to_url(self, url):
        self.driver.get(url)

    def get_element(self, selector):
        selector_name = self.get_selector(selector)
        by, locator = selector_name[0], selector_name[1]
        return self.driver.find_element(by, locator)

    def get_elements(self, selector):
        selector_name = self.get_selector(selector)
        by, locator = selector_name[0], selector_name[1]
        return self.driver.find_elements(by, locator)

    def wait_until_invisible(self, selector_name, interaction=None):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.invisibility_of_element_located(selector),
                                 interaction=interaction)

    def wait_until_visible(self, selector_name, interaction=None):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.visibility_of_element_located(selector),
                                 interaction=interaction)

    def wait_until_present(self, selector_name, interaction=None, time_out=TIMEOUT):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.presence_of_element_located(selector),
                                 interaction=interaction, time_out=time_out)

    def wait_until_clickable(self, selector_name, interaction=None):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.element_to_be_clickable(selector),
                                 interaction=interaction)

    def wait_until_any_element_visible(self, selector_name, interaction=None):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.visibility_of_any_elements_located(selector),
                                 interaction=interaction)

    def __wait_until(self, expected_condition, interaction, time_out=TIMEOUT):
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

        return WebDriverWait(self.driver, time_out).until(expected_condition, message=message)

    def dismiss_popup(self, *args):
        for elem in args:
            try:
                self.driver.execute_script(f"document.querySelector(\'{elem}\').click()")
            except:
                pass

    def get_selector(self, selector_name):
        selector = selector_name.get(self.app_version) if type(selector_name) == dict else selector_name
        if selector is None:
            raise Exception(f'Selector {selector_name} for version {self.app_version} is not found')
        return selector

    def execute_js(self, js):
        return self.driver.execute_script(js)

    @property
    def app_version(self):
        return self.driver.app_version if 'app_version' in dir(self.driver) else None

    @staticmethod
    def generate_random_string(length):
        return "".join([random.choice(string.digits + string.ascii_letters + ' ') for _ in range(length)])
