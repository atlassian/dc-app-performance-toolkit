"""Module with all custom exceptions"""


class WebDriverExceptionPostpone(Exception):
    """
    Class is created to postpone an exception raised from webdriver to first webdriver.get method. Thanks to that BZT
    version >1.16.3 is recognizing tests with a web driver exception as failed.
    """

    def __init__(self, msg: str):
        self.msg = msg

    def get(self, *args, **kwargs):
        """
        Simple method called instead of webdriver.get and raising an exception with a message from a driver exception.

        :param args: args passed to get method
        :param kwargs: kwargs passed to get method
        :return: None - Exception with a message from a driver is raised
        """
        raise Exception(self.msg)
