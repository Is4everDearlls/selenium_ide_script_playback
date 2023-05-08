import abc
from typing import Any


class BaseCollector(metaclass=abc.ABCMeta):
    def collect(self, *args, **kwargs) -> Any:
        pass
