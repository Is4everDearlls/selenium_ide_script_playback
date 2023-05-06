from selenium.webdriver.common.by import By

from framework.operable import BaseWebOperation, BaseTestCase


class BaseSeleniumIDEScript(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Command(BaseSeleniumIDEScript, BaseWebOperation):
    def __init__(self, id, comment, command, target, targets, value, openWindow: bool = False,
                 windowHandlesName: str = '',
                 windowTimeout: int = 10,
                 driver=None):
        super().__init__(id, comment if comment else command)
        self.comment = comment
        self.command = command
        self.driver = driver
        self.target = target
        self.targets = targets
        self.value = value
        self.open_window = openWindow
        self.window_handles_name = windowHandlesName
        self.window_timeout = windowTimeout

    def _get_locator(self):
        keys = {
            "linkText": By.LINK_TEXT,
            "css": By.CSS_SELECTOR,
        }
        by, locator = self.target.split("=", 1)
        return keys.get(by, by), locator

    def open(self):
        self.get(self.target)

    def setWindowSize(self):
        self.driver.maximize_window()

    def click(self, locator=None, timeout=None, message=None, ec=None):
        if self.open_window:
            self.save_window_handles()
        locator = self._get_locator() if not locator else locator
        super().click(locator, timeout, message, ec=None)
        if self.open_window:
            self.wait_and_save_new_window(self.window_handles_name, self.window_timeout)

    def selectWindow(self):
        target = self.target.split("=", 1)[1].replace("${", '').replace("}", '')
        self.switch_to_window(target)

    def type(self):
        self.send_keys(self._get_locator(), self.value)

    def mouseOver(self):
        self.move_to_element(self._get_locator())

    @classmethod
    def execute(cls, driver, method=None, *args, **kwargs):
        instance = cls(*args, **kwargs)
        setattr(instance, "driver", driver)
        setattr(cls, "driver", driver)
        return getattr(instance, instance.command)()


class TestCase(BaseSeleniumIDEScript, BaseTestCase):
    def __init__(self, id, name, *commands: Command):
        super().__init__(id, name)
        self.commands = commands


class TestSuites(BaseSeleniumIDEScript, BaseTestCase):
    def __init__(self, id, name, persistSession: bool, parallel: bool, timeout: int, *tests: TestCase):
        super().__init__(id, name)
        self.persist_session = persistSession
        self.parallel = parallel
        self.timeout = timeout
        self.testcases = tests
