import abc
import json
from json import JSONDecodeError
from typing import Any, List

from selenium.common import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait

from selenium_ide_script.utils import json_data_extract


class BaseCollector(metaclass=abc.ABCMeta):
    def collect(self, *args, **kwargs) -> Any:
        pass


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
                logs.append(ConsoleLog(**log))
        return logs


class NetworkLog(dict):

    def __init__(self):
        super().__init__()

    @property
    def request_id(self):
        return self.get('request_id')

    @property
    def source(self):
        return self.get('source')

    @property
    def url(self):
        return self.get('url')

    @property
    def method(self):
        return self.get('method')

    @property
    def type(self):
        return self.get('type')

    @property
    def request_headers(self):
        return self.get('request_headers', {})

    @property
    def post_data(self):
        return self.get('post_data')

    @property
    def timing(self):
        return self.get('timing')

    @property
    def response_status_code(self):
        return self.get('response_status_code')

    @property
    def response_headers(self):
        return self.get('response_headers', {})

    @property
    def response_body(self):
        return self.get('response_body')

    @property
    def finished(self):
        return self.get('finished')

    @property
    def canceled(self):
        return self.get('canceled')

    @property
    def error(self):
        return self.get('error')

    @property
    def logs(self):
        return self.get('logs')

    def append_chrome_devtools_protocol_log(self, log, driver):
        method = json_data_extract(log, "$.message.message.method")
        if method.startswith("Network"):
            request_id = json_data_extract(log, "$.message.message.params.requestId")
            self._append_log(log)
            self._set_request_id(request_id)
            if method == 'Network.requestWillBeSentExtraInfo':
                self._request_will_be_sent_extra_info(log)
            elif method == 'Network.requestWillBeSent':
                self._request_will_be_sent(log)
            elif method == 'Network.responseReceived':
                self._response_received(log, driver)
            elif method == 'Network.responseReceivedExtraInfo':
                self._response_received_extra_info(log)
            elif method == 'Network.loadingFailed':
                self._loading_failed(log)
            elif method == 'Network.loadingFinished':
                self._loading_finished(log)

    def _request_will_be_sent(self, log):
        self['source'] = json_data_extract(log, "$.message.message.params.documentURL")
        self['url'] = json_data_extract(log, "$.message.message.params.request.url")
        self['method'] = json_data_extract(log, "$.message.message.params.request.method")
        self._set_headers("request_headers", json_data_extract(log, "$.message.message.params.request.headers"))
        self['type'] = json_data_extract(log, "$.message.message.params.type")
        self['post_data'] = json_data_extract(log, "$.message.message.params.request.postData")
        self._set_timing('request', json_data_extract(log, "$.timestamp"))

    def _request_will_be_sent_extra_info(self, log):
        self._set_headers("request_headers", json_data_extract(log, "$.message.message.params.headers"))

    def _response_received(self, log, driver):
        self._set_timing('response', json_data_extract(log, "$.timestamp"))
        self['response_status_code'] = json_data_extract(log, "$.message.message.params.response.status")
        self._set_headers('response_headers', json_data_extract(log, "$.message.message.params.headers"))
        _response_body = {}
        try:
            _response_body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': self.request_id})
            _response_body = json.loads(_response_body.get('body'))
        except WebDriverException as e:
            _response_body = ";".join(e.args)
        except JSONDecodeError:
            _response_body = _response_body.get('body')
        self['response_body'] = _response_body

    def _response_received_extra_info(self, log):
        self._set_headers("response_headers", json_data_extract(log, "$.message.message.params.headers"))
        self['response_status_code'] = json_data_extract(log, "$.message.message.params.statusCode")

    def _loading_finished(self, log):
        self['finished'] = True
        self['canceled'] = False
        self['error'] = None
        self._set_timing('finished', json_data_extract(log, "$.timestamp"))

    def _loading_failed(self, log):
        self['finished'] = True
        self['canceled'] = json_data_extract(log, '$.message.message.params.canceled')
        self['error'] = json_data_extract(log, '$.message.message.params.errorText')
        self._set_timing('finished', json_data_extract(log, "$.timestamp"))

    def _set_headers(self, key, headers):
        if headers and isinstance(headers, dict):
            self[key] = {**self.get(key, {}), **headers}

    def _set_request_id(self, request_id):
        if not self.request_id:
            self['request_id'] = request_id

    def _append_log(self, log):
        if not self.get('logs'):
            self['logs'] = []
        self['logs'].append(log)

    def _set_timing(self, key, value):
        if not self.get('timing'):
            self['timing'] = {}
        self['timing'][key] = value

    def __eq__(self, other):
        if isinstance(other, NetworkLog):
            return other.request_id == self.request_id
        elif isinstance(other, str):
            return other == self.request_id
        else:
            return other.__eq__(self)


class WebDriverNetworkCollector(BaseCollector):
    LOG_TYPE = "performance"
    TIMEOUT = 10

    def __init__(self):
        self.networks = {}

    def collect(self, driver, *args, **kwargs) -> List[NetworkLog]:
        data = WebDriverWait(driver, self.TIMEOUT).until(self)
        return [] if data == -1 else data

    def __call__(self, driver, *args, **kwargs):
        _logs = driver.get_log(self.LOG_TYPE)
        if len(_logs) == 0:
            data = self.networks.copy()
            self.networks.clear()
            return data.values() if len(data.values()) > 0 else -1
        for _log in _logs:
            _log['message'] = json.loads(_log.get("message"))
            method = json_data_extract(_log, "$.message.message.method")
            if method.startswith("Network"):
                request_id = json_data_extract(_log, "$.message.message.params.requestId")
                network = self.networks.get(request_id) if request_id in self.networks.keys() else NetworkLog()
                network.append_chrome_devtools_protocol_log(_log, driver)
                self.networks[request_id] = network
        return False
