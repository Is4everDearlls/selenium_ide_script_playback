import json
from json import JSONDecodeError
from typing import Any, List

from selenium.common import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait

from selenium_ide_script_playback_tools.collector.base import BaseCollector
from selenium_ide_script_playback_tools.utils import json_data_extract


class HttpRequestDetails:

    def __init__(self, *args, **kwargs):
        self.id = None
        self.request = HttpRequest()
        self.response = HttpResponse()
        self.logs = []
        self.loading_status = False
        self.canceled = False
        self.error_text = None

    def __dict__(self):
        return {
            "request_id": self.id,
            "request": self.request,
            "response": self.response,
            "loading_status": self.loading_status,
            "canceled": self.canceled,
            "error_text": self.error_text
        }

    def append_chrome_devtools_protocol_log(self, log, driver):
        method = json_data_extract(log, "$.message.message.method")
        if method.startswith("Network"):
            request_id = json_data_extract(log, "$.message.message.params.requestId")
            if not self.id:
                self.id = request_id
            if method in ['Network.requestWillBeSentExtraInfo', 'Network.requestWillBeSent']:
                self.request.append_network_log(log)
                self.logs.append(log)
            elif method in ['Network.responseReceived', 'Network.responseReceivedExtraInfo']:
                self.response.append_network_log(log, driver)
                self.logs.append(log)
            elif method in ['Network.loadingFinished', 'Network.loadingFailed']:
                self._append_loading_log(log)
                self.logs.append(log)

    def _append_loading_log(self, log):
        method = json_data_extract(log, "$.message.message.method")
        request_id = json_data_extract(log, "$.message.message.params.requestId")
        self.id = self.id if self.id else request_id
        self.loading_status = True
        if method == 'Network.loadingFailed':
            self._loading_failed(log)
        elif method == 'Network.loadingFinished':
            self._loading_finished(log)

    def _loading_finished(self, log):
        self.loading_status = True

    def _loading_failed(self, log):
        self.canceled = json_data_extract(log, '$.message.message.params.canceled')
        self.error_text = json_data_extract(log, '$.message.message.params.errorText')

    def __eq__(self, other):
        if isinstance(other, HttpRequestDetails):
            return other.id == self.id
        elif isinstance(other, str):
            return other == self.id
        elif isinstance(other, HttpRequest):
            return other.request_id == self.id
        elif isinstance(other, HttpResponse):
            return other.request_id == self.id
        else:
            return other.__eq__(self)


class HttpRequest(dict):

    def __init__(self):
        super().__init__()

    @property
    def source(self):
        return self.get("source")

    @property
    def request_id(self):
        return self.get("request_id")

    @property
    def url(self):
        return self.get("url")

    @property
    def method(self):
        return self.get("method")

    @property
    def type(self):
        return self.get("type")

    @property
    def headers(self):
        return self.get("headers")

    @property
    def data(self):
        return self.get("data")

    @property
    def timestamp(self):
        return self.get("timestamp", 0)

    def append_network_log(self, log):
        method = json_data_extract(log, "$.message.message.method")
        request_id = json_data_extract(log, "$.message.message.params.requestId")
        self._set_request_id(request_id)
        if method == 'Network.requestWillBeSentExtraInfo':
            self._request_will_be_sent_extra_info(log)
        elif method == 'Network.requestWillBeSent':
            self._request_will_be_sent(log)

    def _request_will_be_sent(self, log):
        self['source'] = json_data_extract(log, "$.message.message.params.documentURL")
        self['url'] = json_data_extract(log, "$.message.message.params.request.url")
        self['method'] = json_data_extract(log, "$.message.message.params.request.method")
        headers = json_data_extract(log, "$.message.message.params.request.headers")
        if headers:
            self._set_response_headers(headers)
        self['type'] = json_data_extract(log, "$.message.message.params.type")
        self['data'] = json_data_extract(log, "$.message.message.params.request.postData")
        self['timestamp'] = json_data_extract(log, "$.timestamp")

    def _request_will_be_sent_extra_info(self, log):
        headers = json_data_extract(log, "$.message.message.params.headers")
        if headers:
            self._set_response_headers(headers)

    def _set_request_id(self, request_id):
        if not self.request_id:
            self['request_id'] = request_id

    def _set_response_headers(self, headers):
        _headers = self.get('headers', {})
        self['headers'] = {**_headers, **headers}


class HttpResponse(dict):
    def __init__(self):
        super().__init__()

    @property
    def request_id(self):
        return self.get('request_id')

    @property
    def headers(self):
        return self.get('headers')

    @property
    def status_code(self):
        return self.get('status_code')

    @property
    def timestamp(self):
        return self.get('timestamp')

    @property
    def body(self):
        return self.get('body')

    def append_network_log(self, log, driver):
        method = json_data_extract(log, "$.message.message.method")
        request_id = json_data_extract(log, "$.message.message.params.requestId")
        self._set_request_id(request_id)
        if method == 'Network.responseReceived':
            self._response_received(log, driver)
        elif method == 'Network.responseReceivedExtraInfo':
            self._response_received_extra_info(log)

    def _response_received(self, log, driver):
        self['timestamp'] = json_data_extract(log, "$.timestamp")
        self['status_code'] = json_data_extract(log, "$.message.message.params.response.status")
        headers = json_data_extract(log, "$.message.message.params.headers")
        if headers:
            self._set_request_headers(headers)
        request_id = json_data_extract(log, "$.message.message.params.requestId")
        _response_body = {}
        try:
            _response_body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
            _response_body = json.loads(_response_body.get('body'))
        except WebDriverException:
            pass
        except JSONDecodeError:
            _response_body = _response_body.get('body')
        self['body'] = _response_body

    def _response_received_extra_info(self, log):
        headers = json_data_extract(log, "$.message.message.params.headers")
        if headers:
            self._set_request_headers(headers)
        self['status_code'] = json_data_extract(log, "$.message.message.params.statusCode")

    def _set_request_id(self, request_id):
        if not self.request_id:
            self['request_id'] = request_id

    def _set_request_headers(self, headers):
        _headers = self.get('headers', {})
        self['headers'] = {**_headers, **headers}


class WebDriverNetworkCollector(BaseCollector):
    LOG_TYPE = "performance"
    TIMEOUT = 10

    def __init__(self):
        self.http_request_details = {}

    def collect(self, driver, *args, **kwargs) -> List[HttpRequestDetails]:
        data = WebDriverWait(driver, self.TIMEOUT).until(self)
        return [] if isinstance(data,bool) else [d.__dict__() for d in data]

    def __call__(self, driver, *args, **kwargs):
        _logs = driver.get_log(self.LOG_TYPE)
        if len(_logs) == 0:
            data = self.http_request_details.copy()
            self.http_request_details.clear()
            return data.values() if len(data.values()) > 0 else True
        for _log in _logs:
            _log['message'] = json.loads(_log.get("message"))
            method = json_data_extract(_log, "$.message.message.method")
            if method.startswith("Network"):
                request_id = json_data_extract(_log, "$.message.message.params.requestId")
                http_request = self.http_request_details.get(
                    request_id) if request_id in self.http_request_details.keys() else HttpRequestDetails()
                http_request.append_chrome_devtools_protocol_log(_log, driver)
                self.http_request_details[request_id] = http_request
        return False
