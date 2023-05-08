from typing import List

from selenium_ide_script_playback_tools.collector.base import BaseCollector


class ConsoleLog(dict):
    def level(self):
        return self.get('level')

    def message(self):
        return self.get('message')

    def timestamp(self):
        return self.get('timestamp', 0)


class WebDriverConsoleCollector(BaseCollector):

    def collect(self, driver, *args, **kwargs) -> List[ConsoleLog]:
        logs = list()
        for log_type in ["driver", "browser"]:
            for log in driver.get_log(log_type):
                logs.append(ConsoleLog(log))
        return logs
