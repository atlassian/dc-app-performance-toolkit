from selenium_ui.conftest import print_timing

from selenium_ui.jira.pages.pages import SimpleWikiPage, SimpleWikiPageEditor, SimpleWikiPagesList, PopupManager


def sw_page_load(webdriver, datasets):
    page = SimpleWikiPage(webdriver, project_key=datasets['sw_project_key'], page_key=datasets['sw_page_key'])

    @print_timing("selenium_sw_page_load")
    def measure():
        page.go_to()
        page.wait_for_page_loaded()

    measure()
    PopupManager(webdriver).dismiss_default_popup()


def sw_page_edit(webdriver, datasets):
    sw_page_editor = SimpleWikiPageEditor(webdriver, project_key=datasets['sw_project_key'],
                                          page_key=datasets['sw_page_key'])

    @print_timing("selenium_sw_page_edit")
    def measure():
        @print_timing("selenium_sw_page_edit:load_editor")
        def sub_measure():
            sw_page_editor.go_to()
            sw_page_editor.wait_for_page_loaded()

        sub_measure()

        PopupManager(webdriver).dismiss_default_popup()

        @print_timing("selenium_sw_page_edit:editing_page")
        def sub_measure():
            sw_page_editor.change_title()
            sw_page_editor.write_description()

        sub_measure()

        @print_timing("selenium_sw_page_edit:save_page")
        def sub_measure():
            sw_page_editor.save_page()

        sub_measure()

    measure()


def sw_page_create(webdriver, datasets):
    sw_pages_list = SimpleWikiPagesList(webdriver, project_key=datasets['sw_project_key'])

    @print_timing('selenium_sw_page_create')
    def measure():
        @print_timing('selenium_sw_page_create:load_page')
        def sub_measure():
            sw_pages_list.go_to()
            sw_pages_list.wait_for_page_loaded()

        sub_measure()

        @print_timing('selenium_sw_page_create:adding_page')
        def sub_measure():
            sw_pages_list.add_page()
            sw_pages_list.write_title()

        sub_measure()

        @print_timing('selenium_sw_page_create:creating_page')
        def sub_measure():
            sw_pages_list.click_create()

        sub_measure()

    measure()


def sw_add_comment(webdriver, datasets):
    sw_page = SimpleWikiPage(webdriver, project_key=datasets['sw_project_key'], page_key=datasets['sw_page_key'])

    @print_timing('selenium_sw_add_comment')
    def measure():
        @print_timing('selenium_sw_add_comment:load_page')
        def sub_measure():
            sw_page.go_to()
            sw_page.wait_for_page_loaded()

        sub_measure()

        sw_page.add_comment()

        @print_timing('selenium_sw_add_comment:comment_saving')
        def sub_measure():
            sw_page.click_save()

        sub_measure()

    measure()
