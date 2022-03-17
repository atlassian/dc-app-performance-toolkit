import random
import string
from collections import OrderedDict

from packaging import version
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait

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

    def get_selector(self, selector):
        if type(selector) is OrderedDict:
            result = next(iter(selector.items()))[1]
            for sel_version, sel in selector.items():
                selector_version = version.parse(sel_version)
                if self.app_version >= selector_version:
                    result = sel
            return result
        else:
            return selector

    def get_element(self, selector):
        by, locator = selector[0], selector[1]
        return self.driver.find_element(by, locator)

    def get_elements(self, selector):
        by, locator = selector[0], selector[1]
        return self.driver.find_elements(by, locator)

    def element_exists(self, selector):
        by, locator = selector[0], selector[1]
        return True if self.driver.find_elements(by, locator) else False

    def wait_until_invisible(self, selector, timeout=timeout):
        return self.__wait_until(expected_condition=ec.invisibility_of_element_located(selector), time_out=timeout)

    def wait_until_visible(self, selector, timeout=timeout):
        return self.__wait_until(expected_condition=ec.visibility_of_element_located(selector), time_out=timeout)

    def wait_until_available_to_switch(self, selector):
        return self.__wait_until(expected_condition=ec.frame_to_be_available_and_switch_to_it(selector),
                                 time_out=self.timeout)

    def wait_until_present(self, selector, timeout=timeout):
        return self.__wait_until(expected_condition=ec.presence_of_element_located(selector), time_out=timeout)

    def wait_until_clickable(self, selector, timeout=timeout):
        return self.__wait_until(expected_condition=ec.element_to_be_clickable(selector), time_out=timeout)

    def wait_until_any_element_visible(self, selector, timeout=timeout):
        return self.__wait_until(expected_condition=ec.visibility_of_any_elements_located(selector),
                                 time_out=timeout)

    def wait_until_any_ec_presented(self, selectors, timeout=timeout):
        any_ec = AnyEc()
        any_ec.ecs = tuple(ec.presence_of_element_located(selector) for selector in selectors)
        return self.__wait_until(expected_condition=any_ec, time_out=timeout)

    def wait_until_any_ec_text_presented_in_el(self, selector_text_list, timeout=timeout):
        any_ec = AnyEc()
        any_ec.ecs = tuple(ec.text_to_be_present_in_element(locator=selector_text[0], text_=selector_text[1]) for
                           selector_text in selector_text_list)
        return self.__wait_until(expected_condition=any_ec, time_out=timeout)

    def __wait_until(self, expected_condition, time_out=timeout):
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

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()


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
