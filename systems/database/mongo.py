import os
from dotenv import load_dotenv
from os.path import join, dirname
from mongoengine import connect

dotenv_path = join(dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

MONGODB_HOST = os.environ.get('MONGODB_HOST', '127.0.0.1')
MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
MONGODB_DBNAME = os.environ.get('MONGODB_DBNAME', 'pegassus')
MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME', 'root')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'secret')
MONGODB_USE_AUTH = bool(os.environ.get('MONGODB_USE_AUTH', False))

if MONGODB_USE_AUTH:
    ConnectMongo = connect(db=MONGODB_DBNAME, host=MONGODB_HOST, port=MONGODB_PORT,
                           username=MONGODB_USERNAME, password=MONGODB_PASSWORD, authentication_source='admin', connect=False)
else:
    ConnectMongo = connect(db=MONGODB_DBNAME, host=MONGODB_HOST, port=MONGODB_PORT, connect=False)
