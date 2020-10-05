# -*- coding: utf-8 -*-
import datetime
import json

import flask
from bson import json_util, ObjectId, SON, iteritems, text_type
from bson.json_util import DEFAULT_JSON_OPTIONS, default
from flask import Response
from mongoengine import QuerySet
from mongoengine.base import BaseDocument


def neo_json_convert(obj, json_options=DEFAULT_JSON_OPTIONS):
    """Recursive helper method that converts BSON types so they can be
    converted into json.
    """
    if hasattr(obj, 'iteritems') or hasattr(obj, 'items'):  # PY3 support
        return SON(((k, neo_json_convert(v, json_options)) for k, v in iteritems(obj)))

    elif hasattr(obj, '__iter__') and not isinstance(obj, (text_type, bytes)):
        return list((neo_json_convert(v, json_options) for v in obj))

    try:
        obj = default(obj, json_options)
        return obj
    except TypeError:
        return obj


class JSONEncoder(json.JSONEncoder):
    """datetime aware json encoder"""

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        elif isinstance(obj, datetime.date):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return (datetime.datetime.min + obj).time().isoformat()
        elif isinstance(obj, Response):
            return str(obj)
        else:
            return super(JSONEncoder, self).default(obj)


class MongoEngineJSONEncoder(JSONEncoder):
    """json encoder for mongoengine document"""

    def default(self, obj):
        if isinstance(obj, BaseDocument):
            try:
                return neo_json_convert(obj.transform())
            except:
                return neo_json_convert(obj.to_mongo())
        elif isinstance(obj, QuerySet):
            return json_util._json_convert(obj.as_pymongo())
        elif isinstance(obj, ObjectId):
            return str(obj)
        else:
            return super(MongoEngineJSONEncoder, self).default(obj)


def mongo2json(doc) -> str:
    """Convert mongoengine document to json

    :param doc: document to convert
    :type doc: mongoengine.document.Document
    :return: json string
    """
    result = json.dumps(doc, default=json_util.default)
    return result


def override_json_encoder(app):
    """

    :type app: flask.Flask
    """
    app.json_encoder = MongoEngineJSONEncoder
