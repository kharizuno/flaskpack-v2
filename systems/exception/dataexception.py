# -*- coding: utf-8 -*-
from systems.exception.base import NeoException


class DataException(NeoException):
    """Thrown error related to data was occured"""


class DataNotFoundException(DataException):
    """Thrown when data not found"""
    def __init__(self):
        _msg = "No Data Found"
        super(DataNotFoundException, self).__init__(_msg, 404, 404)
