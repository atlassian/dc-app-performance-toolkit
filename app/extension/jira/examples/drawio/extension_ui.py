from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from jira.selenium_ui.conftest import print_timing, application_url

APPLICATION_URL = application_url()
timeout = 20


# This should be called after an issue is viewed.
def custom_action(webdriver, datasets):
    # Click more
    webdriver.find_element_by_id('opsbar-operations_more').click()
    @print_timing
    def measure(webdriver, interaction):
        # Click to add a diagram (opens the drawio editor)
        webdriver.find_element_by_id('drawio-add-menu-item').click()
        WebDriverWait(webdriver, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.ID, 'drawioEditor')))
    measure(webdriver, 'selenium_open_drawio_editor')
