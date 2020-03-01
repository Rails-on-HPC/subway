"""
Exception classes for subway.
"""
# TODO: more organized and hierachical exceptions.


class SubwayException(Exception):
    def __init__(self, message, code=10):
        """

        :param message: str.
        :param code: int. 10 general, 11 jobid unmatch, 12 only valid for general without id
            13 no such atrribute in history of conf
        """
        self.message = message
        self.code = code

    def __str__(self):
        return "%s %s" % (self.__class__.__name__, self.message)


class CLIException(SubwayException):
    def __init__(self, message, code=10):
        super().__init__(message, code)


class MatchError(CLIException):
    def __init__(self, message, code=11):
        super().__init__(message, code)


class NoAttribute(CLIException):
    def __init__(self, message, code=13):
        super().__init__(message, code)


class EndingBubble(SubwayException):
    pass
