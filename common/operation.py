import abc
import uuid

from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as expected
from selenium.webdriver.common.action_chains import ActionChains


class BaseWebOperation(metaclass=abc.ABCMeta):
    DEFAULT_EXPECTED = expected.visibility_of_element_located
    DEFAULT_WAIT_TIMEOUT = 10

    @classmethod
    def _target_processor(cls, target):
        _by_dict = {
            "css": By.CSS_SELECTOR,
            "linkText": By.LINK_TEXT
        }
        if isinstance(target, str) and "=" in target:
            _by, _target = target.split("=", 1)
            return _by_dict.get(_by, _by), _target
        return target

    @classmethod
    def wait_for_find_element(cls, driver, target, timeout=None, message=None, ec=None):
        target = cls._target_processor(target)
        if not ec:
            ec = cls.DEFAULT_EXPECTED
        if not timeout:
            timeout = cls.DEFAULT_WAIT_TIMEOUT
        return WebDriverWait(driver, timeout).until(ec(target), message)

    @classmethod
    def click(cls, driver, target, timeout=None, message=None, ec=None):
        if not message:
            message = "not found element[%s] to click" % str(target)
        cls.wait_for_find_element(driver, target, timeout, message, ec).click()

    @classmethod
    def maximize_window(cls, driver):
        driver.maximize_window()

    @classmethod
    def send_keys(cls, driver, target, value, timeout=None, message=None, ec=None):
        if not message:
            message = "not found element[%s] to input value" % str(target)
        cls.wait_for_find_element(driver, target, timeout, message, ec).send_keys(value)

    @classmethod
    def open(cls, driver, target):
        driver.get(target)

    @classmethod
    def move_to_element(cls, driver, target, timeout=None):
        element = cls.wait_for_find_element(driver, target, timeout)
        ActionChains(driver).move_to_element(element).perform()
        element = cls.wait_for_find_element(driver, "css=body", timeout)
        ActionChains(driver).move_to_element(element).perform()

    @classmethod
    def execute(cls, command, *args, **kwargs):
        if command not in dir(cls):
            raise KeyError("未找到方法%s" % command)
        return getattr(cls(), command)(*args, **kwargs)


class BaseStep(metaclass=abc.ABCMeta):
    def __init__(self, step_id, comment, command, target, value, instance: BaseWebOperation = None, *targets):
        self.instance = BaseWebOperation() if not instance else instance
        self.step_id = step_id if step_id else uuid.uuid4()
        self.result = False
        self.processed = 0
        self.comment = comment
        self.command = command
        self.target = target
        self.value = value
        self.targets = targets

    def invoke(self, driver, *args, **kwargs):
        try:
            self.instance.execute(self.command, driver=driver, *args, **kwargs)
        except TimeoutException:
            pass
        return


class WebDriverLog:
    pass
