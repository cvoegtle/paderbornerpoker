from flask import Flask, request, render_template, make_response

from poker import Table, User

COOKIE_TABLE = "POKER_TABLE"
COOKIE_TABLE_UPDATE = "TABLE_UPDATE"
COOKIE_USER = "POKER_USER_ID"
COOKIE_USER_NAME = "POKER_USER_NAME"

app = Flask(__name__)

users = dict()
tables = dict()

@app.route('/', methods=['GET', 'POST'])
def show_table():
    table = load_table()
    if table is None:
        return render_create_table()
    else:
        return render_table(table)


@app.route('/create_table', methods=['POST'])
def create_table():
    user = create_user(request.form.get('user_name'))
    table = create_new_table(user, request.form.get('table_name'))
    response = render_invite(table)
    set_cookie(response, COOKIE_TABLE, table.identifier)
    set_cookie(response, COOKIE_USER, user.identifier)
    set_cookie(response, COOKIE_USER_NAME, user.name)
    return response


@app.route('/invitation/<int:table_identifier>', methods=['GET'])
def receive_invitation(table_identifier):
    table = load_table_by_id(table_identifier)
    response = render_invitation(table)
    set_cookie(response, COOKIE_TABLE, table.identifier)
    return response


@app.route('/accept_invitation', methods=['POST'])
def accept_invitation():
    table = load_table()
    user = create_user(request.form.get('user_name'))
    table.add_user(user)
    response = render_table(table)
    set_cookie(response, COOKIE_USER, user.identifier)
    set_cookie(response, COOKIE_USER_NAME, user.name)
    return response


@app.route('/clear', methods=['POST'])
def clear_table():
    table = load_table()
    table.clear()
    response = render_table(table)
    return response


@app.route('/show', methods=['POST'])
def show_cards_on_table():
    table = load_table()
    table.show_cards()
    response = render_table(table)
    return response


@app.route('/card/<int:card_key>', methods=['GET', 'POST'])
def play_card(card_key):
    table = load_table()
    user = load_user()
    card = table.cards[card_key]
    table.play_card(user, card)
    response = render_table(table)
    return response


@app.route('/check_for_update', methods=['GET', 'POST'])
def check_for_update():
    table = load_table()
    return str(table.last_update)


def render_table(table):
    rendered_page = render_template('index.html', table=table)
    response = make_response(rendered_page)
    set_cookie(response, COOKIE_TABLE_UPDATE, table.last_update)
    return response


def render_create_table():
    user_name = request.cookies.get(COOKIE_USER_NAME)
    rendered_page = render_template('create_table.html', user_name="" if user_name is None else user_name)
    return make_response(rendered_page)


def render_invite(table):
    rendered_page = render_template('invite.html', url=assemble_invitation_url(table.identifier))
    return make_response(rendered_page)


def assemble_invitation_url(identifier):
    return request.root_url + "invitation/" + str(identifier)


def render_invitation(table):
    user_name = request.cookies.get(COOKIE_USER_NAME)
    rendered_page = render_template('invitation.html', table=table, user_name="" if user_name is None else user_name)
    return make_response(rendered_page)


def create_user(user_name):
    user = User(user_name)
    users[user.identifier] = user
    return user


def create_new_table(user, table_name):
    table = Table(user, table_name)
    tables[table.identifier] = table
    return table


def load_table():
    table_cookie = request.cookies.get(COOKIE_TABLE)
    if table_cookie is None:
        return None
    else:
        table_identifier = int(table_cookie)
        return load_table_by_id(table_identifier)


def load_table_by_id(table_identifier):
    return tables.get(table_identifier)


def load_user():
    user_cookie = request.cookies.get(COOKIE_USER)
    if user_cookie is None:
        return None
    else:
        user_identifier = int(user_cookie)
        return users.get(user_identifier)


def set_cookie(response, cookie, value, max_age=None):
    response.set_cookie(cookie, str(value), samesite='Strict', httponly=False, max_age=max_age)


# Aufwärmanfragen der App Engine annehmen und positiv beantworten, damit immer eine aktive Instanz vorhanden ist
@app.route('/_ah/warmup')
def warmup():
    return '', 200, {}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
