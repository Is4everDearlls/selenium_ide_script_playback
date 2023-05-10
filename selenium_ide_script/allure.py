import allure
from allure_commons.types import AttachmentType


class Step:
    def __init__(self, title):
        self.title = title
        self.contents = []

    class _Content:
        def __init__(self, title, content, content_type: AttachmentType = AttachmentType.TEXT, file: bool = None):
            self.file = file
            self.title = title
            self.content = content
            self.content_type = content_type

        def __call__(self, *args, **kwargs):
            if self.file:
                allure.attach.file(self.content, self.title, self.content_type)
            else:
                allure.attach(self.content, self.title, self.content_type)

    def add_sub_step(self, title, content, content_type: AttachmentType = AttachmentType.TEXT, file: bool = False):
        self.contents.append(self._Content(title, content, content_type, file))

    def write(self):
        with allure.step(self.title):
            for content in self.contents:
                content()


class TestResult:
    def __init__(self, file_name, suite_name, testcase_name, description=None, result=True):
        super().__init__()
        self.file_name = file_name
        self.suite_name = suite_name
        self.testcase_name = testcase_name
        self.description = description
        self.steps = []
        self.result = result

    def write(self):
        allure.dynamic.epic(self.file_name)
        allure.dynamic.story(self.suite_name)
        allure.dynamic.title(self.testcase_name)
        allure.dynamic.description(self.description)
        for step in self.steps:
            step.write()
