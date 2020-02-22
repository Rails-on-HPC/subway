class SubwayException(Exception):
    pass


class CLIException(SubwayException):
    def __init__(self, message, code=10):
        self.message = message
        self.code = code

    def __str__(self):
        print("%s %s" % (self.__class__.__name__, self.message))


class MatchError(CLIException):
    def __init__(self, message, code=11):
        super().__init__(message, code)
