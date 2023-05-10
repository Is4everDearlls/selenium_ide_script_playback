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

    def window_handles(self, key: str = 'window_handles'):
        window_handles = self.driver.window_handles
        if key:
            BaseWebOperation.GLOBAL_WINDOW_HANDLES[key] = window_handles
        return window_handles

    def current_window_handle(self, key: str = None):
        current_window_handle = self.driver.current_window_handle
        if key:
            BaseWebOperation.GLOBAL_WINDOW_HANDLES[key] = current_window_handle
        return current_window_handle

    def wait_new_window_handle(self, key: str = None, timeout: int = 10000):
        window_handles = BaseWebOperation.GLOBAL_WINDOW_HANDLES.get('window_handles')
        if not window_handles:
            window_handles = self.driver.window_handles
        WebDriverWait(self.driver, timeout / 1000).until(expected.new_window_is_opened(window_handles))
        new_window_handles = self.driver.window_handles
        new_window_handle = set(new_window_handles).difference(set(window_handles)).pop()
        if key:
            BaseWebOperation.GLOBAL_WINDOW_HANDLES[key] = new_window_handle
        return new_window_handle

    def switch_to_window(self, handles):
        if handles in BaseWebOperation.GLOBAL_WINDOW_HANDLES.keys():
            self.driver.switch_to.window(BaseWebOperation.GLOBAL_WINDOW_HANDLES.get(handles))
        else:
            self.driver.switch_to.window(handles)

    def close(self):
        self.driver.close()

    def find_element(self, locator, timeout=None, message=None, ec=None):

        def _split_string_locator(_str):
            _keys = {
                "linkText": By.LINK_TEXT,
                "css": By.CSS_SELECTOR,
            }
            _by, _locator = _str.split("=", 1)
            return _keys.get(_by, _by), _locator

        if isinstance(locator, str):
            locator = _split_string_locator(locator)
        if not ec:
            ec = BaseWebOperation.DEFAULT_WAIT_EXPECTED
        if not timeout:
            timeout = BaseWebOperation.DEFAULT_WAIT_TIMEOUT
        return WebDriverWait(self.driver, timeout).until(ec(locator), message)

    def click(self, locator, timeout=None, message=None, ec=None):
        self.find_element(locator, timeout, message, ec).click()

    def maximize_window(self):
        self.driver.maximize_window()

    def send_keys(self, locator, value, timeout=None, message=None, ec=None):
        self.find_element(locator, timeout, message, ec).send_keys(value)

    def get(self, url):
        self.driver.get(url)

    def move_to_element(self, locator, timeout=None, message=None, ec=None):
        self.action_chains().move_to_element(self.find_element(locator, timeout, message, ec)).perform()
        body = self.find_element((By.CSS_SELECTOR, "body"), timeout)
        self.action_chains().move_to_element_with_offset(body, 0, 0).perform()

    def double_click(self, locator, timeout=None, message=None, ec=None):
        web_element = self.find_element(locator, timeout, message, ec)
        self.action_chains().double_click(web_element).perform()

    def action_chains(self):
        return ActionChains(self.driver)

    @classmethod
    def execute(cls, driver, method, *args, **params):
        instance = cls()
        setattr(instance, 'driver', driver)
        return getattr(instance, method)(**params)
