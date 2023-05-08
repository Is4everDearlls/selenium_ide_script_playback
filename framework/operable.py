import abc
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.common.action_chains import ActionChains


class BaseWebOperation(metaclass=abc.ABCMeta):
    DEFAULT_WAIT_EXPECTED = expected.visibility_of_element_located
    DEFAULT_WAIT_TIMEOUT = 10
    GLOBAL_WINDOW_HANDLES = dict()
    driver = None

    @classmethod
    def save_window_handles(cls):
        cls.GLOBAL_WINDOW_HANDLES["window_handles"] = cls.driver.window_handles


    @classmethod
    def wait_and_save_new_window(cls, key, timeout):
        window_handles = cls.GLOBAL_WINDOW_HANDLES["window_handles"]
        WebDriverWait(cls.driver, timeout).until(expected.new_window_is_opened(window_handles))
        new_window_handles = cls.driver.window_handles
        new_window_handle = set(new_window_handles).difference(set(window_handles)).pop()
        cls.GLOBAL_WINDOW_HANDLES[key] = new_window_handle

    @classmethod
    def switch_to_window(cls, handles):
        if handles in cls.GLOBAL_WINDOW_HANDLES.keys():
            cls.driver.switch_to.window(cls.GLOBAL_WINDOW_HANDLES[handles])
        else:
            cls.driver.switch_to.window(handles)

    @classmethod
    def close(cls):
        cls.driver.close()

    @classmethod
    def wait_for_find_element(cls, locator, timeout=None, message=None, ec=None):
        if not ec:
            ec = BaseWebOperation.DEFAULT_WAIT_EXPECTED
        if not timeout:
            timeout = BaseWebOperation.DEFAULT_WAIT_TIMEOUT
        return WebDriverWait(cls.driver, timeout).until(ec(locator), message)

    @classmethod
    def click(cls, locator, timeout=None, message=None, ec=None):
        cls.wait_for_find_element(locator, timeout, message, ec).click()

    @classmethod
    def maximize_window(cls):
        cls.driver.maximize_window()

    def send_keys(self, locator, value, timeout=None, message=None, ec=None):
        self.wait_for_find_element(locator, timeout, message, ec).send_keys(value)

    def get(self, url):
        self.driver.get(url)

    @classmethod
    def move_to_element(cls, locator, timeout=None):
        element = cls.wait_for_find_element(locator, timeout)
        ActionChains(cls.driver).move_to_element(element).perform()
        element = cls.wait_for_find_element((By.CSS_SELECTOR, "body"), timeout)
        ActionChains(cls.driver).move_to_element_with_offset(element, 0, 0).perform()

    @classmethod
    def double_click(cls, locator, timeout=None):
        ActionChains(cls.driver).double_click(cls.wait_for_find_element(locator, timeout)).perform()

    @classmethod
    def action_chains(cls):
        return ActionChains(cls.driver)

    @classmethod
    def execute(cls, driver, method, *args, **kwargs):
        instance = cls()
        setattr(instance, 'driver', driver)
        if method not in dir(instance):
            raise KeyError("未找到方法:%s" % method)
        return getattr(instance, method)(*args, **kwargs)


class BaseTestCase(metaclass=abc.ABCMeta):

    def running(self, driver, *args, **kwargs):
        pass


class BaseExecutionEngine(metaclass=abc.ABCMeta):

    def execute(self, *args, **kwargs):
        pass
