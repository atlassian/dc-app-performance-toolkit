import sys

from extension.jira.extension_ui import sw_page_create
from selenium_ui.conftest import Dataset, webdriver
from selenium_ui.jira.modules import login, log_out
from util.conf import JIRA_SETTINGS
from util.data_preparation import jira_prepare_data

PAGES_LIST = 600

if __name__ == '__main__':
    if len(sys.argv) > 1:
        PAGES_LIST = int(sys.argv[1])
    jira_prepare_data.main()
    dataset = Dataset()
    webdriver = webdriver(JIRA_SETTINGS)
    for i in range(PAGES_LIST):
        login(webdriver, dataset.jira_dataset())
        sw_page_create(webdriver, dataset.jira_dataset())
        log_out(webdriver, dataset.jira_dataset())
