class SeleniumIDEException(Exception):
    pass


class NotFoundCommandException(SeleniumIDEException):
    pass


class CommandExecuteException(SeleniumIDEException):
    pass


class WaitSomethingTimeoutException(SeleniumIDEException):
    pass
