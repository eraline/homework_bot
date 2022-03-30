# my custom exceptions

class UnexpectedResponseCode(Exception):
    """The response code is not 200"""
    pass

class NoneInMandatoryValue(Exception):
    """Mandatory value is None"""
    pass


class InvalidTokens(Exception):
    """Token is invalid"""
    pass
