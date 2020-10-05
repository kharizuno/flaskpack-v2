# -*- coding: utf-8 -*-
from systems.exception.base import NeoBadRequestException


class ParamException(NeoBadRequestException):
    """Thrown when validation error occur on parameter"""

    def __init__(self, message=None):
        _msg = "Mandatory Parameter is Required"  #: default message
        message = message or _msg

        super(ParamException, self).__init__(message)


class InvalidParamException(ParamException):
    def __init__(self, message=None):
        _msg = "Parameter Value is Invalid"
        message = message or _msg

        super(InvalidParamException, self).__init__(message)
