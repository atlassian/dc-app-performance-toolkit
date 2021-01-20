from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select
import random
import string

TIMEOUT = 20


class BasePage:
    page_url = ''
    page_loaded_selector = {}
    timeout = TIMEOUT

    def __init__(self, driver):
        self.driver = driver

    def go_to(self):
        self.driver.get(self.page_url)

    def wait_for_page_loaded(self):
        if type(self.page_loaded_selector) == list:
            for selector in self.page_loaded_selector:
                self.wait_until_visible(selector, timeout=self.timeout)
        else:
            self.wait_until_visible(self.page_loaded_selector, timeout=self.timeout)

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

    def element_exists(self, selector):
        selector_name = self.get_selector(selector)
        by, locator = selector_name[0], selector_name[1]
        return self.driver.find_elements(by, locator) is not None

    def wait_until_invisible(self, selector_name):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.invisibility_of_element_located(selector))

    def wait_until_visible(self, selector_name, timeout=TIMEOUT):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.visibility_of_element_located(selector), time_out=timeout)

    def wait_until_available_to_switch(self, selector_name):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.frame_to_be_available_and_switch_to_it(selector),
                                 time_out=self.timeout)

    def wait_until_present(self, selector_name, time_out=TIMEOUT):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.presence_of_element_located(selector), time_out=time_out)

    def wait_until_clickable(self, selector_name):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.element_to_be_clickable(selector), time_out=self.timeout)

    def wait_until_any_element_visible(self, selector_name):
        selector = self.get_selector(selector_name)
        return self.__wait_until(expected_condition=ec.visibility_of_any_elements_located(selector),
                                 time_out=self.timeout)

    def wait_until_any_ec_presented(self, selector_names):
        origin_selectors = []
        for selector in selector_names:
            origin_selectors.append(self.get_selector(selector))
        any_ec = AnyEc()
        any_ec.ecs = tuple(ec.presence_of_element_located(origin_selector) for origin_selector in origin_selectors)
        return self.__wait_until(expected_condition=any_ec)

    def wait_until_any_ec_text_presented_in_el(self, selector_names):
        origin_selectors = []
        for selector_text in selector_names:
            selector = self.get_selector(selector_text[0])
            text = selector_text[1]
            origin_selectors.append((selector, text))
        any_ec = AnyEc()
        any_ec.ecs = tuple(ec.text_to_be_present_in_element(locator=origin_selector[0], text_=origin_selector[1]) for
                           origin_selector in origin_selectors)
        return self.__wait_until(expected_condition=any_ec)

    def __wait_until(self, expected_condition, time_out=TIMEOUT):
        message = f"Error in wait_until: "
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
            except(WebDriverException, Exception):
                pass

    def return_to_parent_frame(self):
        return self.driver.switch_to.parent_frame()

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

    def select(self, element):
        return Select(element)

    def action_chains(self):
        return ActionChains(self.driver)


class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """

    def __init__(self, *args):
        self.ecs = args

    def __call__(self, w_driver):
        for fn in self.ecs:
            try:
                if fn(w_driver):
                    return True
            except(WebDriverException, Exception):
                pass
