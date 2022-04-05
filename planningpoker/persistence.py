import json

from google.cloud import datastore
from google.cloud.datastore import Key

from poker import User, Table, Card
from datetime import datetime as dt


# users = dict()
# tables = dict()
#
#
# def create_user(user_name, is_admin=False):
#     user = User(user_name, is_admin=is_admin)
#     users[user.identifier] = user
#     return user
#
# def retrieve_user(user_identifier):
#     return users.get(user_identifier)
#
#
# def create_table(user, table_name):
#     table = Table(user, table_name)
#     tables[table.identifier] = table
#     return table
#
#
# def retrieve_table(table_identifier):
#     return tables.get(int(table_identifier))
#
#
# def store_table(table):
#     pass
#

APPENGINE_PROJECT = 'effortpoker'

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
    table.identifier = entity.key.id
    return table


def update_table_add_user(table_identifier, user):
    with datastore_client.transaction():
        entity, table = load_and_decode(table_identifier)
        table.add_user(user)
        encode_and_store(entity, table)


def update_table_clear(table_identifier):
    with datastore_client.transaction():
        entity, table = load_and_decode(table_identifier)
        table.clear()
        encode_and_store(entity, table)


def update_table_show_cards(table_identifier):
    with datastore_client.transaction():
        entity, table = load_and_decode(table_identifier)
        table.show_cards()
        encode_and_store(entity, table)


def update_table_play_card(table_identifier, user, card_key):
    with datastore_client.transaction():
        entity, table = load_and_decode(table_identifier)
        card = table.cards[card_key]
        table.play_card(user, card)
        encode_and_store(entity, table)


def load_and_decode(table_identifier):
    entity = retrieve_entity(TABLE_POKER_TABLE, table_identifier)
    table = decode_table(entity)
    print(f'load {table}')
    return entity, table


def encode_and_store(entity, table):
    table.save_time = f'{dt.now()}'
    json_text = json.dumps(table, cls=TableEncoder)
    print(f'store {table}')
    entity[ATTRIBUTE_JSON] = json_text
    datastore_client.put(entity)


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
        return decode_table(entity)


def decode_table(entity):
    table = json.JSONDecoder(object_hook=decode_json_table).decode(entity[ATTRIBUTE_JSON])
    table.identifier = entity.key.id
    return table


def retrieve_entity(table_name, identifier):
    key = Key(table_name, int(identifier), project=APPENGINE_PROJECT)
    entity = datastore_client.get(key)
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
        if isinstance(o, Table):
            dictionary = o.__dict__
            dictionary['users'] = o.users
            dictionary['played_cards'] = o.played_cards
            dictionary['card_value_visible'] = o.card_value_visible
            return dictionary
        if isinstance(o, set):
            return list(o)
        else:
            return o.__dict__


def decode_json_table(json_object):
    if 'key' in json_object and 'value' in json_object and 'text' in json_object:
        card = Card(json_object['key'], json_object['value'], json_object['text'])
        return card
    elif 'name' in json_object and 'is_admin' in json_object:
        user = User(json_object['name'], is_admin=json_object['is_admin'])
        user.identifier = json_object['identifier']
        return user
    elif 'description' in json_object and 'card_value_visible' in json_object:
        table = Table()
        if 'identifier' in json_object:
            table.identifier = json_object['identifier']
        if 'card_value_visible' in json_object:
            table.card_value_visible = json_object['card_value_visible']
        if 'description' in json_object:
            table.description = json_object['description']
        if 'last_update' in json_object:
            table.last_update = json_object['last_update']
        if 'save_time' in json_object:
            table.save_time = json_object['save_time']
        if 'users' in json_object:
            json_users = json_object['users']
            table.users = set(json_users)
        return table
    else:
        return json_object
