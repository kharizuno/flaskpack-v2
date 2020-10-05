# -*- coding: utf-8 -*-
from systems.exception.base import NeoException


class FileException(NeoException):
    """thrown when any error related to filesystem occured"""
    def __init__(self, message=''):
        super(FileException, self).__init__(message)
