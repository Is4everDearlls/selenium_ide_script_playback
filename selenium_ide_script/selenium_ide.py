import json
import time
from enum import Enum
from typing import Union, List, Dict

import allure
from allure_commons.types import AttachmentType
from selenium.webdriver.common.by import By

from selenium_ide_script.allure import TestResult, Step
from selenium_ide_script.collector import WebDriverNetworkCollector, WebDriverConsoleCollector
from selenium_ide_script.operable import BaseWebOperation


class BaseSeleniumIDEScript(dict):
    def __init__(self, id, name, **kwargs):
        super().__init__()
        self['id'] = id
        self['name'] = name

    @property
    def id(self):
        return self.get('id')

    @property
    def name(self):
        return self.get('name')

    def __eq__(self, other):
        if isinstance(other, str):
            return self.id == other
        else:
            return other.__eq__(self)


class Command(BaseSeleniumIDEScript, BaseWebOperation):

    def __init__(self, command, target=None, value=None, id=None, comment='', targets=None, opensWindow=False,
                 windowHandleName='',
                 windowTimeout=10, driver=None):
        super().__init__(id, command)
        self['comment'] = comment
        self['command'] = command
        self['target'] = target
        self['targets'] = targets
        self['value'] = value
        self['opens_window'] = opensWindow
        self['window_handle_name'] = windowHandleName
        self['window_timeout'] = windowTimeout
        self['details'] = {}
        self.result = False
        self.driver = driver

    @property
    def target(self):
        return self.get('target')

    @property
    def command(self):
        return self.get('command')

    @property
    def value(self):
        return self.get('value')

    @property
    def comment(self):
        return self.get('comment')

    @property
    def id(self):
        return self.get('id')

    @property
    def open_window(self):
        return self.get('opens_window', False)

    @property
    def window_handle_name(self):
        return self.get('window_handle_name')

    @property
    def details(self):
        return self.get('details', {})

    @property
    def window_timeout(self):
        return self.get('window_timeout')

    def open(self):
        self.driver.get(self.target)

    def setWindowSize(self):
        return self.maximize_window()

    def close(self):
        pass

    def click(self, locator=None, timeout=None, message=None, ec=None):
        if self.open_window:
            self.window_handles("window_handles")
            self.current_window_handle('root')
        self.find_element(self.target, timeout, message, ec).click()
        if self.open_window:
            self.wait_new_window_handle(self.window_handle_name, self.window_timeout)
            self.switch_to_window(self.window_handle_name)

    def selectWindow(self):
        def split_windows_handle(expr):
            return expr.split("=", 1)[1].replace("${", '').replace("}", '')

        handle = split_windows_handle(self.target)
        self.switch_to_window(handle)

    def storeWindowHandle(self):
        self.switch_to_window(self.target)

    def type(self):
        self.find_element(self.target).send_keys(self.value)

    def mouseOver(self):
        self.move_to_element(self.target)

    @classmethod
    def execute(cls, driver, command, target=None, value=None, id=None, comment='', targets=None, opensWindow=False,
                windowHandleName='',
                windowTimeout=10, *args, **kwargs):
        start = int(time.monotonic() * 1000)
        instance = cls(command, target, value, id, comment, targets, opensWindow, windowHandleName, windowTimeout)
        try:
            setattr(instance, 'driver', driver)
            getattr(instance, instance.command)()
            requests = WebDriverNetworkCollector().collect(driver)
            instance['details']['requests'] = [] if isinstance(requests, bool) else requests
            instance['details']['consoles'] = WebDriverConsoleCollector().collect(driver)
            end = int(time.monotonic() * 1000)
            instance.result = True
        except Exception as e:
            instance['details']['exception'] = ";".join(e.args)
            end = time.monotonic()
            instance.result = False
        instance['details']['timestamp'] = end - start
        return instance


class TestCase(BaseSeleniumIDEScript):

    def __init__(self, id, name, commands):
        super().__init__(id, name)
        self['commands'] = list(commands)
        self.steps = []

    @property
    def commands(self):
        return self.get('commands')

    def running(self, file_name, suite_name, driver):
        result = TestResult(file_name, suite_name, self.name, True)
        for command in self.commands:
            command = Command.execute(driver, **command)
            if command.comment:
                step = Step(f"{command.comment} -> {command.result}")
            else:
                step = Step(f"{command.command} -> {command.result}")
            for network in command.details.get('requests', []):
                if network.type in ['xhr', 'XHR']:
                    step.add_sub_step(f'XHR:[{network.response_status_code}]:{network.url}',
                                      json.dumps(network.response_body, ensure_ascii=False), AttachmentType.JSON)
            for console in command.details.get('consoles', []):
                if console.level == 'SEVERE':
                    step.add_sub_step(f'Console:{console.message}', json.dumps(console), AttachmentType.JSON)
            result.steps.append(step)
            if not command.result:
                result.result = False
        return result


class TestSuites(BaseSeleniumIDEScript):
    def __init__(self, id, name, persistSession, parallel, timeout, tests, **kwargs):
        super().__init__(id, name, **kwargs)
        self['persist_session'] = persistSession
        self['parallel'] = parallel
        self['timeout'] = timeout
        self['tests'] = tests

    @property
    def persist_session(self):
        return self.get("persistSession", False)

    @property
    def parallel(self):
        return self.get("parallel", False)

    @property
    def timeout(self):
        return self.get("timeout", 10)

    @property
    def tests(self):
        return self.get("tests", [])

    def running(self, file_name, driver):
        results = []
        for test in self.tests:
            results.append(TestCase(**test).running(file_name, self.name, driver))
        return results


class SeleniumIDEScriptFile(BaseSeleniumIDEScript):

    def __init__(self, id, name, tests, suites, **kwargs):
        super().__init__(id, name, **kwargs)
        self['tests'] = tests
        self['suites'] = suites

    @property
    def url(self):
        return self.get('url')

    @property
    def tests(self):
        return self.get('tests', [])

    @property
    def suites(self) -> List[TestSuites]:
        data = {}
        suites = []
        for test in self.tests:
            data[test.get('id')] = test
        for suite in self.get('suites', []):
            for index, test in enumerate(suite.get('tests', [])):
                suite['tests'][index] = data.get(test).copy()
            suites.append(suite)
        return suites

    def running(self, driver):
        result = []
        for suite in self.suites:
            result.extend(TestSuites(**suite).running(self.name, driver))
        return result
