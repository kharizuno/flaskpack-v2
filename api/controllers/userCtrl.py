from flask import request, jsonify, make_response, current_app
from flask_jwt import jwt_required, current_identity
from flask_restful import Resource, reqparse

from bson import ObjectId

from systems.exception.base import NeoException
from systems.exception.dataexception import DataNotFoundException

from api.models.userMod import UserMod


class UserAll(Resource):
    @jwt_required()
    def get(self):
        data = request.args

        perpage = int(data['limit']) if 'limit' in data else current_app.config.get('DATA_PER_PAGE', 10)
        page = int(data['page']) if 'page' in data else 0
        offset = (page - 1) * perpage if page > 1 else 0
        offset = offset if 'page' in data else {'unlimited': True}

        keyword = data['keyword'] if 'keyword' in data else ''
        sortby = data['sortby'] if 'sortby' in data else '_id'
        sortby = '_id' if sortby == 'id' else sortby
        sortdir = data['sortdir'] if 'sortdir' in data else 'desc'
        showdelete = True if 'showdelete' in data and data['showdelete'] == '1' else False

        filter = {}
        for d in data:
            if d not in ['page', 'limit', 'sortby', 'sortdir', 'keyword', 'showdelete']:
                filter.update({d: data[d]})

        if (current_identity['company'] and '_id' in current_identity['company'][0]):
            filter.update({'cid': current_identity['company'][0]['_id']})

        Users = UserMod.list(offset, perpage, keyword, filter, sortby, sortdir, showdelete)
        if Users and 'count' in Users and Users['count'] > 0:
            stack = []
            for d in Users['data']:
                stack.append(UserMod.transform(d, filter))

            data = {
                'data': stack,
                'meta': {
                    'count': Users['count']
                }
            }

            return make_response(jsonify(data))

        raise DataNotFoundException


class UserGet(Resource):
    @jwt_required()
    def get(self, idx):
        if idx:
            data = request.args
            dd = ['data', 'page', 'limit', 'sortby', 'sortdir', 'keyword', 'showdelete']

            ff = ''
            filter = {}
            for d in data:
                if d not in dd:
                    ff = d
                    dd.append(d)
                    filter.update({d: data[d]})
            dd.remove('data')

            if (current_identity['company'] and '_id' in current_identity['company'][0]):
                filter.update({'cid': current_identity['company'][0]['_id']})

            field = '_id'
            for d in data:
                if data[d] != '' and data[d] != 'id' and d not in dd:
                    field = data[d]

            field = 'users' if idx == 'me' else field
            idx = current_identity['_id'] if idx == 'me' else idx
            if field == '_id' and not ObjectId.is_valid(idx):
                return make_response(jsonify({'message': 'ID is not valid'}))

            if field != 'id':
                perpage = int(data['limit']) if 'limit' in data else current_app.config.get('DATA_PER_PAGE', 10)
                page = int(data['page']) if 'page' in data else 0
                offset = (page - 1) * perpage if page > 1 else 0
                offset = offset if 'page' in data else {'unlimited': True}

                keyword = data['keyword'] if 'keyword' in data else ''
                sortby = data['sortby'] if 'sortby' in data else '_id'
                sortdir = data['sortdir'] if 'sortdir' in data else 'desc'
                showdelete = True if 'showdelete' in data and data['showdelete'] == '1' else False

            ex = UserMod.listdata(idx, field, offset, perpage, sortby, sortdir, keyword, filter, showdelete)
            if not ex:
                current_app.logger.info(field+": %s does not exist" % idx)
                ex = {'message': 'Data is not available'}

            if field != 'id':
                if ex and 'count' in ex and ex['count'] > 0:
                    stack = []
                    for d in ex['data']:
                        stack.append(UserMod.transform(d, filter))

                    data = {
                        'data': stack,
                        'meta': {
                            'count': ex['count']
                        }
                    }

                    return make_response(jsonify(data))

            return make_response(jsonify(UserMod.transform(ex, filter)))

        raise DataNotFoundException


class UserRegister(Resource):
    def post(self):
        # file = request.files
        data = request.get_json()
        if not data:
            data = request.form

        parser = reqparse.RequestParser()
        parser.add_argument('phone', required=True, help='Phone')
        parser.add_argument('username', required=True, help="Username")
        parser.add_argument('password', required=True, help="Password")

        try:
            ex = UserMod.create(data)
            return make_response(jsonify(UserMod.transform(ex, {})))

        except AttributeError:
            raise

        except Exception as e:
            current_app.logger.error(str(e))
            raise NeoException(str(e))


class UserCreate(Resource):
    @jwt_required()
    def post(self):
        # file = request.files
        data = request.get_json()
        if not data:
            data = request.form

        parser = reqparse.RequestParser()
        parser.add_argument('name', required=False, help="Name")
        parser.add_argument('address', required=False, help='Address')
        parser.add_argument('phone', required=False, help='Phone')
        parser.add_argument('email', required=False, help="Email")
        parser.add_argument('username', required=True, help="Username")
        parser.add_argument('password', required=True, help="Password")
        parser.add_argument('level', required=False, help="Level")
        parser.add_argument('is_active', required=False, help='Active user')

        try:
            ex = UserMod.create(data)
            return make_response(jsonify(UserMod.transform(ex, {})))

        except AttributeError:
            raise

        except Exception as e:
            current_app.logger.error(str(e))
            raise NeoException(str(e))


class UserUpdate(Resource):
    @jwt_required()
    def put(self, idx):
        data = request.get_json()
        if not data:
            data = request.form

        try:
            ex = UserMod.update(idx, data)
            return make_response(jsonify(UserMod.transform(ex, {})))

        except AttributeError:
            raise

        except Exception as e:
            current_app.logger.error(str(e))
            raise NeoException(str(e))


class UserDelete(Resource):
    @jwt_required()
    def delete(self, idx):
        data = request.get_json()
        if not data:
            data = request.form

        if idx:
            if not ObjectId.is_valid(idx):
                return make_response(jsonify({'message': 'ID is not valid'}))

            ex = UserMod.listdata(idx, '_id')
            if not ex:
                current_app.logger.info("ID _id: %s does not exist" % idx)
                ex = {'message': 'Data is not available'}
                return make_response(jsonify(ex))

            temp = False if 'temp' in data and data['temp'] == '0' else True
            ex = UserMod.delete(idx, temp, current_identity)
            if 'err' in ex and ex['err']:
                return make_response(jsonify({'message': ex['err']}))

            ex = {'message': 'Data successfully deleted'}
            return make_response(jsonify(ex))

        raise DataNotFoundException
