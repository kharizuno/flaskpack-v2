from mongoengine import Document, StringField, IntField, EmailField, LongField, BooleanField, ListField, ReferenceField, DateTimeField, \
                        ObjectIdField, DoesNotExist, NotUniqueError, ValidationError, Q
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime
import json

from bson import ObjectId

from systems.exception.base import NeoException
from systems.helpers import datetimeutils
from systems.helpers.crypto import encryt_passhash, compare_passhash
from systems.helpers.datetimeutils import datetime2epoch, epoch2datetime
from systems.helpers.stringutils import slugify

import logging
log = logging.getLogger(__name__)

class UserMod(Document):
    """schema and index definition for collection 'users'

    isActive: 0 = inactive, 1 = active
    """
    meta = {
        'collection': 'users',
        'index_background': True,
        'index_drop_dups': True,
        'index_cls': False,
        'index_options': {
            'collation': {
                'locale': 'id'
            }
        },
        'strict': False,
        'indexes': [
            '#name',
            'branchs',
            'isDeleted',
            'isActive',
            '-createdAt',
            '-updatedAt',
            {
                'fields': ['username'],
                'unique': True
            },
        ]
    }

    companyId = ObjectIdField(required=True)
    branchs = ListField(default=[])
    name = StringField(required=False, max_length=256)
    address = StringField(required=False, max_length=256)
    phone = StringField(required=False, max_length=15)
    email = StringField(required=False, max_length=256)
    username = StringField(required=False, max_length=256, unique=True)
    password = StringField(required=True, max_length=256)
    level = StringField(required=False, max_length=50)
    authOtp = StringField(required=False, max_length=256)
    loginAt = LongField(required=False, default=0)
    createdAt = LongField(default=datetimeutils.get_current_epoch())
    updatedAt = LongField(default=datetimeutils.get_current_epoch())
    isDeleted = BooleanField(default=False)
    isActive = BooleanField(default=True)

    def models():
        return UserMod._get_collection()

    def fields(f, rev=False):
        if rev:
            f = '_id' if f == 'users' else f
            f = 'cid' if f == 'companyId' else f
            f = 'factor' if f == 'authOtp' else f
            f = 'login_at' if f == 'loginAt' else f
            f = 'created_at' if f == 'createdAt' else f
            f = 'updated_at' if f == 'updatedAt' else f
            f = 'active' if f == 'isActive' else f
            f = 'delete' if f == 'isDeleted' else f
        else:
            f = '_id' if f == 'users' else f
            f = 'companyId' if f == 'cid' else f
            f = 'authOtp' if f == 'factor' else f
            f = 'loginAt' if f == 'login_at' else f
            f = 'createdAt' if f == 'created_at' else f
            f = 'updatedAt' if f == 'updated_at' else f
            f = 'isActive' if f in ['active', 'is_active'] else f
            f = 'isDeleted' if f in ['delete', 'is_deleted'] else f

        return f

    def list(skip, count, keyword='', filter='', sortby='_id', sortdir='desc', showdelete=False, listdata=False):
        # ## Standard Query
        # try:
        #     skip = int(skip) if isinstance(skip, int) else skip
        #     count = int(count)
        # except ValueError:
        #     skip = 0
        #     count = 10

        # direction = '+'
        # if sortdir == 'desc':
        #     direction = "-"

        # sorter = "{}{}".format(direction, sortby)

        ## Aggregation Query
        try:
            skip = int(skip) if isinstance(skip, int) else skip
            count = int(count)
        except ValueError:
            skip = 0
            count = 10

        if isinstance(skip, int):
            limit = {"$limit": count}
            skip = {"$skip": skip}

        sortdir = -1 if sortdir == 'desc' else +1
        sorter = {
            "$sort": {
                sortby: sortdir
            }
        }

        count = {"$count": "count"}
        aggsCompany = {
            '$lookup': {
                'from': 'companies',
                'localField': 'companyId',
                'foreignField': '_id',
                'as': 'company'
            }
        }
        aggsBranch = {
            '$lookup': {
                'from': 'branchs',
                'localField': 'branchs',
                'foreignField': '_id',
                'as': 'branchs'
            }
        }

        try:
            query = {}
            if keyword:
                query = {
                    "$and": [
                        {
                            "$or": [
                                {
                                    "name": {
                                        "$regex": "{}.*".format(keyword),
                                        "$options": "i"
                                    }
                                },
                                {
                                    "address": {
                                        "$regex": "{}.*".format(keyword),
                                        "$options": "i"
                                    }
                                },
                                {
                                    "phone": {
                                        "$regex": "{}.*".format(keyword),
                                        "$options": "i"
                                    }
                                },
                                {
                                    "email": {
                                        "$regex": "{}.*".format(keyword),
                                        "$options": "i"
                                    }
                                },
                                {
                                    "username": {
                                        "$regex": "{}.*".format(keyword),
                                        "$options": "i"
                                    }
                                }
                            ]
                        }
                    ]
                }

                if listdata:
                    query['$and'].append(listdata)
            else:
                if listdata:
                    query.update(listdata)

            if keyword:
                query['$and'].append({'isDeleted': showdelete})
            else:
                query.update({'isDeleted': showdelete})

            if filter:
                regex = True if 'regex' in filter else False
                for f in filter:
                    fx = ObjectId(filter[f]) if ObjectId.is_valid(filter[f]) else filter[f]

                    active = True if f == 'active' and fx == '1' else False
                    fx = active if f == 'active' else fx

                    delete = True if f == 'delete' and fx == '1' else False
                    fx = delete if f == 'delete' else fx
                    
                    if f in ['users', 'branchs'] and not ObjectId.is_valid(filter[f]):
                        if len(fx.split(',')) > 0:
                            dxx = []
                            for x in fx.split(','):
                                dxx.append(ObjectId(x))
                            fx = {'$in': dxx}
                    
                    if regex and not ObjectId.is_valid(filter[f]):
                        fill = {UserMod.fields(f): {
                            "$regex": "{}.*".format(fx),
                            "$options": "i"
                        }}
                    else:
                        fill = {UserMod.fields(f): fx}

                    if f not in ['regex']:
                        if keyword:
                            query['$and'].append(fill)
                        else:
                            query.update(fill)

            # ## Standard Query
            # model = UserMod.objects(__raw__=query)
            # # model = UserMod.objects(Q(isDeleted=False))

            # numrows = model.count()
            # data = model.order_by(sorter)

            # if isinstance(skip, int):
            #     data = data.skip(skip).limit(count)

            # if data:
            #     return {
            #         'data': list(data),  # json.loads(data.to_json())
            #         'count': numrows
            #     }

            ## Aggregation Query
            query = {"$match": query} if query else {}
            aggs = [aggsCompany, aggsBranch]
            nums = [aggsCompany, aggsBranch]
            if query:
                aggs.append(query)
                nums.append(query)

            aggs.extend([sorter])
            nums.extend([count])

            if '$skip' in skip:
                aggs.extend([skip, limit])
            
            data = UserMod.objects.aggregate(*aggs)
            numrows = UserMod.objects.aggregate(*nums)            

            if data:
                return {
                    'data': list(data),  # json.loads(data.to_json())
                    'count': list(numrows)[0]['count']
                }

            return data
        except Exception:
            pass

    def listdata(id, field, skip='', count='', sortby='_id', sortdir='desc', keyword='', filter='', showdelete=False):
        try:
            if field != '' and field != '_id':
                val = id
                val = ObjectId(id) if ObjectId.is_valid(id) else val
                if field in ['users', 'branchs']:
                    if ObjectId.is_valid(id):
                        idx = ObjectId(id)
                    else:
                        if len(id.split(',')) > 0:
                            dxx = []
                            for x in id.split(','):
                                dxx.append(ObjectId(x))
                            idx = {'$in': dxx}

                    val = idx if field in ['users', 'branchs'] else val

                active = True if field == 'active' and id.lower() == 'true' else False
                val = active if field == 'active' else val

                delete = True if field == 'delete' and id.lower() == 'true' else False
                val = delete if field == 'delete' else val

                query = {UserMod.fields(field): val}
            else:
                query = {'_id': ObjectId(id)}

            if field == '_id':
                if filter:
                    for f in filter:
                        fx = ObjectId(filter[f]) if ObjectId.is_valid(filter[f]) else filter[f]

                        active = True if f == 'active' and fx == '1' else False
                        fx = active if f == 'active' else fx

                        delete = True if f == 'delete' and fx == '1' else False
                        fx = delete if f == 'delete' else fx
                        
                        query.update({UserMod.fields(f): fx})
                data = UserMod.objects(__raw__=query).first()
            else:
                return UserMod.list(skip, count, keyword, filter, sortby, sortdir, showdelete, query)

            return data  # json.loads(data.to_json())
        except Exception:
            pass

    def create(dt):
        try:
            cid = ObjectId(dt['cid']) if 'cid' in dt and dt['cid'] != '' else ''
            
            branchs = []
            if 'branchs' in dt:
                branchs = dt['branchs'] if isinstance(dt['branchs'], list) else json.loads(dt['branchs'])
                branchs = branchs if dt['branchs'] != '' else []
                dx = []
                for d in branchs:
                    dx.append(ObjectId(d))
                branchs = dx

            name = dt['name'] if 'name' in dt and dt['name'] != '' else ''
            address = dt['address'] if 'address' in dt and dt['address'] != '' else ''
            phone = dt['phone'] if 'phone' in dt and dt['phone'] != '' else ''
            email = dt['email'] if 'email' in dt and dt['email'] != '' else ''
            username = dt['username'] if 'username' in dt and dt['username'] != '' else ''
            password = encryt_passhash(dt['password']) if 'password' in dt and dt['password'] != '' else ''
            level = dt['level'] if 'level' in dt and dt['level'] != '' else 'user'

            if 'is_active' in dt:
                if dt['is_active'] != '':
                    isActive = True if 'is_active' in dt and dt['is_active'] == '1' else False
                else:
                    isActive = True
            else:
                isActive = True

            ex = UserMod(
                companyId=cid,
                branchs=branchs,
                name=name,
                address=address,
                phone=phone,
                email=email,
                username=username,
                password=password,
                level=level,
                createdAt=datetimeutils.get_current_epoch(),
                updatedAt=datetimeutils.get_current_epoch(),
                isActive=isActive,
                isDeleted=False
            )

            ex.save()
            ex = ex.reload()
            return ex  # json.loads(ex.to_json())

        except ValidationError as e:
            return {'message': e.to_dict()}

    def update(idx, dt):
        try:
            set = {}
            for d in dt:
                if dt[d] != '':
                    val = ObjectId(dt[d]) if ObjectId.is_valid(dt[d]) else dt[d]

                    if d == 'branchs':
                        branchs = dt[d] if isinstance(dt[d], list) else json.loads(dt[d])
                        branchs = branchs if dt['branchs'] != '' else []
                        dx = []
                        for n in branchs:
                            dx.append(ObjectId(n))
                        val = dx

                    password = dt[d] if d == 'password' and dt['password'] != '' else []
                    val = encryt_passhash(password) if d == 'password' else val

                    isActive = True if d == 'is_active' and dt[d] == '1' else False
                    val = isActive if d == 'is_active' else val

                    isDeleted = True if d == 'is_deleted' and dt[d] == '1' else False
                    val = isDeleted if d == 'is_deleted' else val

                    set.update({UserMod.fields(d): val})  # NOTE: Update Native
                    # query.append('set__'+a+'='+val)  # NOTE: Update One

            set.update({'updatedAt': datetimeutils.get_current_epoch()})

            # Native Update
            id = {'_id': ObjectId(idx)}
            data = {
                "$set": set
            }
            UserMod.models().update(id, data)
            # UserMod.objects(id=idx).update_one(query, True)

            return UserMod.listdata(idx, '_id')

        except Exception:
            pass

    def delete(idx, temp=True, uid=False):
        try:
            if temp:
                if uid and 'role' in uid and uid['role'] == 'member' or uid and 'level' in uid and uid['level'] == 'superuser':
                    id = {'_id': ObjectId(idx)}
                    data = {
                        "$set": {
                            "isDeleted": True
                        }
                    }
                    UserMod.models().update(id, data)
            else:
                if uid and 'role' in uid and uid['role'] == 'admin' or uid and 'level' in uid and uid['level'] == 'superuser':
                    UserMod.objects(id=idx).delete()
                else:
                    return {"err": "Sorry, You don't have access"}

            return {"err": False}

        except Exception:
            pass

    def transform(dt, filter):
        ex = {}
        for d in dt:
            if d not in ['password']:
                val = dt[d]
                val = epoch2datetime(dt[d]) if d == 'loginAt' else val
                val = epoch2datetime(dt[d]) if d == 'createdAt' else val
                val = epoch2datetime(dt[d]) if d == 'updatedAt' else val
                
                ex.update({UserMod.fields(d, True): val})

        return ex

    def login(identifier, password):
        try:
            u = UserMod.objects(
                    (Q(username=identifier) | Q(email=identifier)) & 
                    Q(isActive=True) & Q(isDeleted=False)
                ).first()

            if not u:
                raise DoesNotExist

            if compare_passhash(password, u.password):
                #: password match, renew last_login
                u.loginAt = datetimeutils.get_current_epoch()
                u.save().reload()

                return u

        except DoesNotExist:
            log.info("No user exist for email/username: %s" % identifier)

        except ServerSelectionTimeoutError as e:
            log.error("Couldn't connect to db server. %es" % e.details)

        return None
