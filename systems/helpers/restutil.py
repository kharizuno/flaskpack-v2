# -*- coding: utf-8 -*-
from flask import jsonify


def make_response(response, code=200, message='success'):
    """naive response formatter

    :type response: dict
    :type code: int
    :type message: success
    :rtype: flask.wrappers.Response
    """
    meta = {}
    data = response

    if isinstance(response, dict):
        if 'meta' in response.keys():
            meta = response.get('meta')

        if 'data' in response.keys():
            data = response.get('data', {})
            if 'message' in data.keys():
                message = data.pop('message')

            if 'code' in data.keys():
                code = data.pop('code')

    response = jsonify({
        'code': code,
        'message': message,
        'data': data,
        'meta': meta
    })
    response.status_code = code
    return response
