import json

from selenium.webdriver import Chrome, DesiredCapabilities

from selenium_ide_script_playback_tools.selenium_ide.testcase import Command


def json_data_reader(json_file):
    with open(json_file, encoding='utf-8') as f:
        return json.load(f)


if __name__ == '__main__':
    data = json_data_reader("selenium_ide_script.side")
    url = data.get("url")
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    caps["excludeSwitches"] = ['enable-automation', 'enable-logging']
    commands = []
    with Chrome(desired_capabilities=caps) as driver:
        for test in data.get("tests"):
            for command in test.get("commands"):
                if command.get("command") == 'open' and command.get('target') == '/':
                    command["target"] = url
                if command.get("command") == "mouseOut":
                    continue
                try:
                    command = Command.execute(driver, **command)
                    commands.append(command)
                except Exception as e:
                    command.data['exception'] = list(e.args)
                    break
    for command in commands:
        for request in command.data.get("requests"):
            if request.get("request").get('type') == 'XHR':
                print(request)
