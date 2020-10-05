# -*- coding: utf-8 -*-
import json
import logging
import logging.config
import os
from flask import Flask
from flask_cors import CORS

from systems.libraries import handler
from systems.exception.base import NeoException
from systems.helpers import jsonutil

"""Initialize HTTP Instance"""
server = Flask("FlaskPack", instance_relative_config=True)
server.config.from_object('systems.config.NeoConfig')

#: connect MySQL
from systems.database.mysql import configMySQL
db = configMySQL(server)

#: connect MongoDB
from systems.database.mongo import ConnectMongo
ConnectMongo

#: initialize REST API
from systems.config.route import jwt, api

#: initialize JWT
jwt.init_app(server)

from api.routes import apiRoutes
apiRoutes(api)
api.init_app(server)

#: initialize error handler
server.register_error_handler(404, handler.not_found_handler)
server.register_error_handler(405, handler.not_allowed_handler)
server.register_error_handler(Exception, handler.python_exc_handler)  #: core python exception
server.register_error_handler(NeoException,
                                handler.default_error_handler)  #: core application exception

#: override json_encoder
jsonutil.override_json_encoder(server)

# #: setup logging
# __setup_logging()

from werkzeug.contrib.fixers import ProxyFix
server.wsgi_app = ProxyFix(server.wsgi_app)
CORS(server)


def __setup_logging():
    """setup logging to file"""
    homedir = os.environ['HOME']
    debug = os.environ.get('DEBUG', True)
    version = "devel" if debug else "prod"

    loglocation = os.path.join(
        homedir,
        "logs",
        "flashpack",
        'flashpack_{}.log'.format(version)
    )

    log_dir = os.path.dirname(loglocation)
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    base_config = os.path.join(os.path.dirname(__file__), '../', 'etc', 'log_config.json')

    with open(base_config, 'r') as f:
        conf = json.loads(f.read())

    conf['handlers']['file_handler']['filename'] = loglocation
    conf['handlers']['file_handler']['level'] = 'DEBUG' if debug else "WARN"
    conf['handlers']['stream_handler']['level'] = 'DEBUG' if debug else "WARN"

    logging.config.dictConfig(conf)
