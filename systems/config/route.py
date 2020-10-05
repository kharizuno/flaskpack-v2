from flask_restful import Api

#: Route API
api = Api(prefix='/api/v1', catch_all_404s=False)


#: Route JWT Auth
import json
from datetime import datetime

from flask import request, current_app
from flask_jwt import JWT, JWTError, _jwt
from jwt import decode as jwt_decode

from api.models.memberMod import MemberMod
from api.models.userMod import UserMod

def identity_handler(payload):
    # user_id = payload.get('user_id')
    # u = MemberMod.listdata(user_id, '_id')
    # if not u:
    #     u = UserMod.listdata(user_id, '_id')

    # return u

    return payload


def auth_handler(username, password):
    u = MemberMod.login(username, password)
    if not u:
        u = UserMod.login(username, password)
        if not u:
            raise JWTError('Bad Request', 'Invalid Credentials')

    return u


def payload_creator(identity):
    """create payload to use with flask-jwt

    :type identity: User
    :return: identity payload
    """
    iat = datetime.utcnow()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')

    payload = {
        'iat': iat,
        'exp': exp,
        'nbf': nbf,
        'user_id': str(identity.id),
        'identity': {
            'user_id': str(identity.id),
            'name': identity.name,
            'username': identity.username
        }
    }
    return payload


def auth_request_callback():
    data = request.get_json()
    if not data:
        data = request.form
        data = data if 'username' in list(data) or 'email' in list(data) else json.loads(list(data)[0])
    
    if not data:
        raise JWTError('Bad Request', 'No Credentials')

    idx = 'username' if 'username' in data else 'email'
    username = data.get(idx, None)
    password = data.get('password', None)
    criterion = [username, password, len(data) == 2]

    if not all(criterion):
        raise JWTError('Bad Request', 'Invalid credentials')

    identity = _jwt.authentication_callback(username, password)

    if identity:
        access_token = _jwt.jwt_encode_callback(identity)
        return _jwt.auth_response_callback(access_token, identity)
    else:
        raise JWTError('Bad Request', 'Invalid credentials')


def auth_request_handler():
    auth_header_value = request.headers.get('Authorization', None)
    auth_header_prefix = current_app.config['JWT_AUTH_HEADER_PREFIX']

    if not auth_header_value:
        return

    parts = auth_header_value.split()

    if parts[0].lower() != auth_header_prefix.lower():
        raise JWTError('Invalid JWT header', 'Unsupported authorization type')
    elif len(parts) == 1:
        raise JWTError('Invalid JWT header', 'Token missing')
    elif len(parts) > 2:
        raise JWTError('Invalid JWT header', 'Token contains spaces')

    return parts[1]


def jwt_decode_handler(token):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']
    leeway = current_app.config['JWT_LEEWAY']

    verify_claims = current_app.config['JWT_VERIFY_CLAIMS']
    required_claims = current_app.config['JWT_REQUIRED_CLAIMS']

    options = {
        'verify_' + claim: True
        for claim in verify_claims
    }

    options.update({
        'require_' + claim: True
        for claim in required_claims
    })

    mapping = jwt_decode(token, secret, options=options, algorithms=[algorithm], leeway=leeway)
    uid = mapping.get('identity', {}).get('user_id', None)

    x = 'member'
    u = MemberMod.listdata(uid, 'members')
    if not u:
        x = 'user'
        u = UserMod.listdata(uid, 'users')
        if not u:
            raise JWTError(
                'Authorization Required',
                'Invalid Authorization',
                status_code=403,
                headers={'WWW-Authenticate': 'JWT realm="access_token"'}
            )

    if u and 'count' in u and u['count'] > 0:
        # stack = []
        # for d in u['data']:
        #     if x == 'member':
        #         stack.append(MemberMod.transform(d, filter))
        #     else:
        #         stack.append(UserMod.transform(d, filter))
            
        # u = stack[0]
        u = u['data'][0]
        if not u['isActive']:
            raise JWTError(
                'Authorization Required',
                'Your user is not active',
                status_code=403,
                headers={'WWW-Authenticate': 'JWT realm="access_token"'}
            )

    if not u:
        return mapping
    else:
        return u


jwt = JWT(None, auth_handler, identity_handler)

#. Login (Return Data User)
jwt.jwt_payload_callback = payload_creator
jwt.auth_request_callback = auth_request_callback

#. Check JWT (When used every url)
jwt.request_callback = auth_request_handler
jwt.jwt_decode_callback = jwt_decode_handler