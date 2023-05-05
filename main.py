import json

from selenium.webdriver import Chrome

from pagechecker_pro.selenium_ide.testcase import Command


def json_data_reader(json_file):
    with open(json_file, encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    data = json_data_reader("SeleniumIDEScript.side")
    url = data.get("url")
    for test in data.get("tests"):
        with Chrome() as driver:
            for command in test.get("commands"):
                if command.get("command") == 'open':
                    command["target"] = url
                if command.get("command") == "mouseOut":
                    continue
                Command.execute(driver, **command)
