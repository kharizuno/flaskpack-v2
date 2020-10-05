# -*- coding: utf-8 -*-


class NeoException(Exception):
    """Base Exception for Neo Project"""

    def __init__(self, message, http_code=500, error_code=500, payload=None):
        super(NeoException, self).__init__(message)

        self.message = message
        self.http_code = http_code
        self.code = error_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['code'] = self.code
        rv['message'] = self.message
        rv['data'] = {}

        return rv


class NeoBadRequestException(NeoException):
    """thrown when bad request were received"""

    def __init__(self, message="Bad, Bad Request"):
        super(NeoBadRequestException, self).__init__(message, http_code=400, error_code=400, payload=None)
