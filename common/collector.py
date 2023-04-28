import enum
from typing import AnyStr, Union
import abc


class CollectorKeys(enum.Enum):
    SCREENSHOT = "screen_shot"
    LOG = "log"


class BaseCollector(metaclass=abc.ABCMeta):
    """
    收集器, 用于测试过程中收集测试数据
    """
    pass

    @abc.abstractmethod
    def data(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def save_key(self) -> Union[CollectorKeys, AnyStr]:
        pass


class CollectionController:
    def __init__(self, *collectors: BaseCollector):
        self.collectors = collectors
        self.data = {}

    def data(self):
        for collector in self.collectors:
            self.data[collector.save_key()] = collector.data()

    class Screenshot(BaseCollector):
        def data(self, driver, *args, **kwargs):
            return driver.get_screenshot_as_base64()

        def save_key(self) -> Union[CollectorKeys, AnyStr]:
            return CollectorKeys.SCREENSHOT.value

    class Log(BaseCollector):
        def __init__(self, level, timestamp, identification, *args, **kwargs):
            self.level = level
            self.timestamp = timestamp
            self.identification = identification

        @abc.abstractmethod
        def message(self):
            pass

        def data(self):
            return {
                self.identification: [{"level": self.level, "message": self.message(), "timestamp": self.timestamp}]}

    class Network(Log):
        def __init__(self, request_id, level, message, timestamp):
            super().__init__(level, message, timestamp)
            self.request_id = request_id

        @abc.abstractmethod
        def method(self):
            pass

        def __eq__(self, other):
            if isinstance(other, Network):
                return self.request_id == other.request_id
            elif isinstance(other, str):
                return self.method().__eq__(other) or self.request_id.__eq__(other)

    class RequestWillBeSent(Network):
        def save_key(self) -> Union[CollectorKeys, AnyStr]:
            pass

        def __init__(self, request_id, identification, level, message, timestamp):
            super().__init__(request_id, identification, level, message, timestamp)

        def message(self):
            pass

        def method(self):
            return "Network.requestWillBeSent"

    class RequestWillBeSentExtraInfo(Network):
        def method(self):
            return "Network.requestWillBeSentExtraInfo"

        def message(self):
            pass

    class DataReceived(Network):
        def method(self):
            return "Network.dataReceived"

        def message(self):
            pass

    class ResponseReceivedExtraInfo(Network):
        def method(self):
            return "Network.responseReceivedExtraInfo"

        def message(self):
            pass

    class ResponseReceived(Network):
        def method(self):
            return "Network.responseReceived"

        def message(self):
            pass

    class LoadingFinished(Network):
        def method(self):
            return "Network.responseReceived"

        def message(self):
            pass

    class LoadingFailed(Network):
        def method(self):
            return "Network.loadingFailed"
