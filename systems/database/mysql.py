import os
from dotenv import load_dotenv
from os.path import join, dirname
from flask_sqlalchemy import SQLAlchemy

dotenv_path = join(dirname(__file__), '../..', '.env')
load_dotenv(dotenv_path)

MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
MYSQL_DBNAME = os.environ.get('MYSQL_DBNAME', 'pegassus')
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'secret')

def configMySQL(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + str(MYSQL_USERNAME) + ':' + str(MYSQL_PASSWORD) + '@' + str(MYSQL_HOST) + '/' + str(MYSQL_DBNAME)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db = SQLAlchemy(app)

    return db