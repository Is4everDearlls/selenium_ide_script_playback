import abc

from selenium_ide.content import Command


class Verifiable(Command, metaclass=abc.ABCMeta):
    pass


class VerifyByWebDriver(Verifiable):

    def __init__(self, driver=None, **kwargs):
        super(VerifyByWebDriver, self).__init__(**kwargs)
        self.driver = driver

    def execute(self, *args, **kwargs):
        return getattr(self, self.command)()

    def verifyChecked(self):
        return self.driver.is_selected()

    def verifyNotChecked(self):
        return not self.driver.is_selected()

    def verifyEditable(self):
        pass

    def verifyNotEditable(self):
        pass

    def verifyElementPresent(self):
        pass

    def verifyElementNotPresent(self):
        pass

    def verifySelectedValue(self):
        pass

    def verifyNotSelectedValue(self):
        pass

    def verifyNotText(self):
        pass

    def verifySelectedLabel(self):
        pass

    def verifyText(self):
        pass

    def verifyValue(self):
        pass

    def verifyTitle(self):
        pass


class VerifyByData(Verifiable):
    def execute(self, *args, **kwargs):
        pass

    def verify(self):
        pass
