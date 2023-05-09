import abc

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.common.action_chains import ActionChains


class BaseWebOperation(metaclass=abc.ABCMeta):
    DEFAULT_WAIT_EXPECTED = expected.visibility_of_element_located
    DEFAULT_WAIT_TIMEOUT = 10
    GLOBAL_WINDOW_HANDLES = dict()

    def __init__(self, driver=None):
        self.driver = driver

    def window_handles(self, key='window_handles', single=True):
        if single:
            self.GLOBAL_WINDOW_HANDLES[key] = self.driver.current_window_handle
        else:
            self.GLOBAL_WINDOW_HANDLES[key] = self.driver.window_handles
        return self.GLOBAL_WINDOW_HANDLES.get(key)

    def wait_for_new_window(self, fn, key, timeout, *args, **kwargs):
        self.window_handles('window_handles')
        fn(*args, **kwargs)
        window_handles = self.GLOBAL_WINDOW_HANDLES["window_handles"]
        WebDriverWait(self.driver, timeout).until(expected.new_window_is_opened(window_handles))
        new_window_handles = self.driver.window_handles
        new_window_handle = set(new_window_handles).difference(set(window_handles)).pop()
        self.GLOBAL_WINDOW_HANDLES[key] = new_window_handle

    def switch_to_window(self, handles):
        if handles in self.GLOBAL_WINDOW_HANDLES.keys():
            self.driver.switch_to.window(self.GLOBAL_WINDOW_HANDLES.get(handles))
        else:
            self.driver.switch_to.window(handles)

    def close(self):
        self.driver.close()

    def wait_for_find_element(self, locator, timeout=None, message=None, ec=None):
        if not ec:
            ec = BaseWebOperation.DEFAULT_WAIT_EXPECTED
        if not timeout:
            timeout = BaseWebOperation.DEFAULT_WAIT_TIMEOUT
        return WebDriverWait(self.driver, timeout).until(ec(locator), message)

    def click(self, locator, timeout=None, message=None, ec=None):
        self.wait_for_find_element(locator, timeout, message, ec).click()

    def maximize_window(self):
        self.driver.maximize_window()

    def send_keys(self, locator, value, timeout=None, message=None, ec=None):
        self.wait_for_find_element(locator, timeout, message, ec).send_keys(value)

    def get(self, url):
        self.driver.get(url)

    def move_to_element(self, locator, timeout=None, message=None, ec=None):
        element = self.wait_for_find_element(locator, timeout, message, ec)
        self.action_chains().move_to_element(element).perform()
        element = self.wait_for_find_element((By.CSS_SELECTOR, "body"), timeout)
        self.action_chains().move_to_element_with_offset(element, 0, 0).perform()

    def double_click(self, locator, timeout=None, message=None, ec=None):
        web_element = self.wait_for_find_element(locator, timeout, message, ec)
        self.action_chains().double_click(web_element).perform()

    def action_chains(self):
        return ActionChains(self.driver)

    @classmethod
    def execute(cls, driver, method, **params):
        instance = cls()
        setattr(instance, 'driver', driver)
        return getattr(instance, method)(**params)
