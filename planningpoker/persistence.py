from poker import User, Table

users = dict()
tables = dict()


def create_user(user_name, is_admin=False):
    user = User(user_name, is_admin=is_admin)
    users[user.identifier] = user
    return user


def create_table(user, table_name):
    table = Table(user, table_name)
    tables[table.identifier] = table
    return table


def retrieve_table(table_identifier):
    return tables.get(table_identifier)


def retrieve_user(user_identifier):
    return users.get(user_identifier)


