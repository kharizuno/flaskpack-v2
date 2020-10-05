from flask import request, jsonify, make_response
from functools import wraps
import jwt

from systems.config import NeoConfig
from api.models.user import User

def tokenize(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)

        try:
            data = jwt.decode(token, NeoConfig.SECRET_KEY)
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return make_response(jsonify({'message': 'Token is invalid!'}), 401)

        return f(current_user, *args, **kwargs)

    return decorated