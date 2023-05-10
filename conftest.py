import json
from selenium.webdriver import DesiredCapabilities, Chrome

from selenium_ide_script.selenium_ide import SeleniumIDEScriptFile
from selenium_ide_script.utils import update_chromedriver_version


def pytest_generate_tests(metafunc):
    update_chromedriver_version()
    result = []
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    caps["excludeSwitches"] = ['enable-automation', 'enable-logging']

    with Chrome(desired_capabilities=caps) as driver:
        with open('selenium_ide_script.side', encoding='utf-8') as f:
            file = SeleniumIDEScriptFile(**json.load(f))
            result.extend(file.running(driver))
    metafunc.parametrize("testcase", result)
