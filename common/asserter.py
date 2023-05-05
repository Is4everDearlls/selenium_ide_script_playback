import abc
import json
from json import JSONDecodeError
from typing import Union, List, Dict, Set, AnyStr, Tuple

import jsonpath as jsonpath


class BaseAsserter(metaclass=abc.ABCMeta):
    """
    断言器基类
    """

    @abc.abstractmethod
    def asserting(self, *args, **kwargs) -> bool:
        """ 断言抽象方法，子类实现该方法进行断言 """
        pass


class JSONDataAsserter(BaseAsserter):

    def __init__(self, expression, expect):
        self.expression = expression
        self.expect = expect

    def asserting(self, data: Union[List, Dict, Set, Tuple, AnyStr], *args, **kwargs) -> bool:
        if isinstance(data, Set):
            data = list(data)
        if isinstance(data, bytes) or isinstance(data, str):
            try:
                data = json.loads(data)
            except JSONDecodeError:
                return False
        data = self.extract(data)
        return data == self.expect

    @abc.abstractmethod
    def extract(self, data, *args, **kwargs):
        return jsonpath.jsonpath(data, self.expression)
