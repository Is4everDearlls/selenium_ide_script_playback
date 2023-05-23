import abc

from selenium_ide.content import Command


class WebOperable(Command):

    def execute(self, *args, **kwargs):
        pass
