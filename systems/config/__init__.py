# -*- coding: utf-8 -*0
import os
from datetime import timedelta
from dotenv import load_dotenv
from os.path import join, dirname

from systems.helpers import jsonutil

dotenv_path = join(dirname(__file__), '../..', '.env')
load_dotenv(dotenv_path)

# MONGODB_HOST = os.environ.get('MONGODB_HOST', '127.0.0.1')
# MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
# MONGODB_DBNAME = os.environ.get('MONGODB_DBNAME', 'pegassus')
# MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', 'root')
# MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'secret')
# MONGODB_USE_AUTH = bool(os.environ.get('MONGODB_USE_AUTH', False))


class NeoConfig:
    #: flask
    DEBUG = os.environ.get('DEBUG', False)

    PORT = int(os.environ.get('PORT', 8008))

    SECRET_KEY = '99c4d1a10249369bd252e1945a04021c9ae11a5a208' \
                 '407345b6df88a360e31f14b747a40fe2a666576ffc5' \
                 'f58ae036ec26ff65044f7d44c623a9c388f88f9fae'

    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/var/www/html')
    ALLOWED_EXTENSIONS = tuple(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

    # #: MySQL
    # MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    # MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    # MYSQL_DBNAME = os.environ.get('MYSQL_DBNAME', 'pegassus')
    # MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'root')
    # MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'secret')
    # SQLALCHEMY_DATABASE_URI = 'mysql://' + str(MYSQL_USERNAME) + ':' + str(MYSQL_PASSWORD) + '@' + str(MYSQL_HOST) + '/' + str(MYSQL_DBNAME)
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    #: pagination
    DATA_PER_PAGE = 10

    #: category pair to content
    __enable_category = str(os.getenv('ENABLE_CATEGORY', False))
    if __enable_category == 'False' or __enable_category == '0':
        ENABLE_CATEGORY = False
    else:
        ENABLE_CATEGORY = True

    THUMBOR_URL = os.environ.get("THUMBOR_URL", "http://localhost:8000")

    #: flask jwt
    JWT_AUTH_USERNAME_KEY = 'username'
    __jwt_expiration_delta = int(os.environ.get('JWT_EXPIRATION_DELTA', 600))
    JWT_EXPIRATION_DELTA = timedelta(seconds=__jwt_expiration_delta)

    DATABASE_HOST = os.environ.get("DATABASE_HOST", 'localhost')
    DATABASE_USER = os.environ.get("DATABASE_USER", 'root')
    DATABASE_PASS = os.environ.get("DATABASE_PASS", '')
    DATABASE_NAME = os.environ.get("DATABASE_NAME", '')

    #: rabbitMQ
    MQ_HOST = os.environ.get("MQ_HOST", "localhost")
    MQ_PORT = int(os.environ.get("MQ_PORT", "5672"))
    MQ_USER = os.environ.get("MQ_USER", "guest")
    MQ_PASSWORD = os.environ.get("MQ_PASSWORD", "guest")
    MQ_VHOST = os.environ.get("MQ_VHOST", "/")

    # MQTopics_CRAWLER_DATA = "pegassus.crawler.data"
    # MQTopics_IMAGE_CDN = "pegassus.image.cdn"
    # MQTopics_CRAWLER_SOCIAL_DATA = "pegassus.crawler.social.data"
    # MQTopics_POSTPROCESSED_DATA = "pegassus.postprocessed.data"
    # MQTopics_POSTPROCESSED_DATA_TEXT = "pegassus.postprocessed.data.text"

    #: flask_restful
    BUNDLE_ERRORS = True
    RESTFUL_JSON = {
        'separators': (',', ':'),
        'indent': 2,
        'cls': jsonutil.MongoEngineJSONEncoder
    }

    if DEBUG:
        TESTING = True
    else:
        TESTING = False

    @classmethod
    def AMQP_DSN(cls):
        return
