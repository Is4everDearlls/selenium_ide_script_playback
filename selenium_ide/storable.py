import abc

from selenium_ide.content import Command


class Storable(Command, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def operation(self, *args, **kwargs):
        pass
