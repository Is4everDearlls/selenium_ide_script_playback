import json

from selenium.webdriver import Chrome, DesiredCapabilities

from common.operation import BaseWebOperation

if __name__ == '__main__':
    # 环境检查
    # 参数预设
    # 生成执行器
    # 生成测试用例
    # 执行测试用例
    # 生成测试报告
    # with open("xuanwu.side", encoding='utf-8') as file:
    #     data = json.load(file)
    #     for test in data.get("tests"):
    #         with Chrome() as driver:
    #             commands = test.get("commands")
    #             for command in commands:
    #                 print(command)
    #                 target = command.get("target")
    #                 operation = command.get("command")
    #                 if operation == "open":
    #                     driver.get(target)
    #                 if command.get("command") == "click":
    #                     target = target.split("=")
    #                     by, locator = target[0], target[1]
    #                     if by == "css":
    #                         by = "css selector"
    #                     if by == "linkText":
    #                         by = "link text"
    #                     element = find_element(driver, (by, locator))
    #                     element.click()
    #                     print("点击:%s" % element.text)
    #                 if command.get("command") == "type":
    #                     target = target.split("=")
    #                     by, locator = target[0], target[1]
    #                     if by == "css":
    #                         by = "css selector"
    #                     print("输入:%s" % command.get("value"))
    #                     find_element(driver, (by, locator)).send_keys(command.get("value"))
    caps = DesiredCapabilities.CHROME
    caps['goog:loggingPrefs'] = {'performance': 'ALL'}
    caps["excludeSwitches"] = ['enable-automation', 'enable-logging']
    with Chrome(desired_capabilities=caps) as driver:
        operator = BaseWebOperation()
        operator.execute("open", driver=driver, target="https://test-online.ibaibu.com")
        operator.execute("click", driver=driver, target="id=tab-2")
        operator.execute("send_keys", driver=driver, target='xpath=//*[@id="pane-2"]/form/div[1]/div/div/input',
                         value="廖加权")
        for log in driver.get_log("performance"):
            log = json.loads(log.get("message")).get("message")
            if log.get("method").startswith("Network"):
                print(log)
