class BaseTestCase(metaclass=abc.ABCMeta):
    def __init__(self, testcase_id: str, name: str, *steps: BaseStep):
        self.testcase_id = testcase_id
        self.name = name
        self.steps = steps

    @abc.abstractmethod
    def testing(self, driver, *args, **kwargs):
        pass