import json

from google.cloud import datastore
from google.cloud.datastore import Key

from poker import User, Table


# users = dict()
# tables = dict()
#
#
# def create_user(user_name, is_admin=False):
#     user = User(user_name, is_admin=is_admin)
#     users[user.identifier] = user
#     return user
#
#
# def create_table(user, table_name):
#     table = Table(user, table_name)
#     tables[table.identifier] = table
#     return table
#
#
# def retrieve_table(table_identifier):
#     return tables.get(table_identifier)
#
#
# def retrieve_user(user_identifier):
#     return users.get(user_identifier)
#
APPENGINE_PROJECT = 'paderbornerpoker'

TABLE_USER = 'user'
TABLE_POKER_TABLE = 'poker_table'
ATTRIBUTE_JSON = 'json'

datastore_client = datastore.Client()


def create_user(user_name, is_admin=False):
    user = User(user_name, is_admin=is_admin)
    with datastore_client.transaction():
        entity = datastore.Entity(key=datastore_client.key(TABLE_USER), exclude_from_indexes=[ATTRIBUTE_JSON])
        entity[ATTRIBUTE_JSON] = json.dumps(user, cls=UserEncoder)
        datastore_client.put(entity)
    print(entity.key)
    user.identifier = entity.key.id
    return user


def retrieve_user(user_identifier):
    with datastore_client.transaction():
        entity = retrieve_entity(TABLE_USER, user_identifier)
    if entity is None:
        return None
    else:
        user = json.JSONDecoder(object_hook=decode_json_user).decode(entity[ATTRIBUTE_JSON])
        user.identifier = entity.key.id
        return user


def create_table(user, table_name):
    table = Table(user, table_name)
    with datastore_client.transaction():
        entity = datastore.Entity(key=datastore_client.key(TABLE_POKER_TABLE), exclude_from_indexes=[ATTRIBUTE_JSON])
        entity[ATTRIBUTE_JSON] = json.dumps(table, cls=TableEncoder)
        datastore_client.put(entity)
    print(entity.key)
    table.identifier = entity.key.id
    return table


def store_table(table):
    with datastore_client.transaction():
        entity = retrieve_entity(TABLE_POKER_TABLE, table.identifier)
        entity[ATTRIBUTE_JSON] = json.dumps(table, cls=TableEncoder)
        datastore_client.put(entity)


def retrieve_table(table_identifier):
    with datastore_client.transaction():
        entity = retrieve_entity(TABLE_POKER_TABLE, table_identifier)
    if entity is None:
        return None
    else:
        table = json.JSONDecoder(object_hook=decode_json_table).decode(entity[ATTRIBUTE_JSON])
        table.identifier = entity.key.id
        return table


def retrieve_entity(table_name, identifier):
    key = Key(table_name, int(identifier), project=APPENGINE_PROJECT)
    print(f'retrieve {key}')
    entity = datastore_client.get(key)
    print(f'entity: {entity}')
    return entity


class UserEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def decode_json_user(json_object):
    user = User()
    for key in json_object:
        user.__setattr__(key, json_object[key])
    return user


class TableEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def decode_json_table(json_object):
    table = Table()
    return table
