import abc


class Content(dict, metaclass=abc.ABCMeta):
    @property
    def id(self):
        return self.get('id')

    @property
    def name(self):
        return self.get('name')


class Command(Content):
    @property
    def comment(self):
        return self.get('comment', '')

    @property
    def command(self):
        return self.get('command', '')

    @property
    def target(self):
        return self.get('target', '')

    @property
    def targets(self):
        return self.get('targets', [])

    @property
    def value(self):
        return self.get('value', '')

    @property
    def opens_window(self):
        return self.get('opensWindow', False)

    @property
    def window_handle_name(self):
        return self.get('windowHandleName', '')

    @property
    def window_timeout(self):
        return self.get('windowTimeout', 2000)

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        pass


class TestCase(Content):
    @property
    def commands(self):
        return self.get('commands', [])


class TestSuite(Content):
    @property
    def persist_session(self):
        return self.get('persistSession', False)

    @property
    def parallel(self):
        return self.get('parallel', False)

    @property
    def timeout(self):
        return self.get('timeout', 3)

    @property
    def tests(self):
        return self.get('tests', [])


class SeleniumIDE(Content):
    @property
    def version(self):
        return self.get("version")

    @property
    def url(self):
        return self.get("url")

    @property
    def tests(self):
        return self.get("tests", [])

    @property
    def suites(self):
        return self.get("suites", [])

    @property
    def urls(self):
        return self.get("urls", [])

    @property
    def plugins(self):
        return self.get("plugins", [])
