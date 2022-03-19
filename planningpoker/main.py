from flask import Flask, request, render_template, make_response

from poker import Table, User

COOKIE_TABLE = "POKER_TABLE"
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
    response = render_table(table)
    set_cookie(response, COOKIE_USER_NAME, user.name)
    return response


@app.route('/clear', methods=['POST'])
def clear_table():
    table = load_table()
    table.clear()
    return render_table(table)


@app.route('/show', methods=['POST'])
def show_cards_on_table():
    table = load_table()
    table.show_cards()
    return render_table(table)


@app.route('/card/<int:card_key>', methods=['POST'])
def start(card_key):
    table = load_table()
    user = load_user()
    card = table.cards[card_key]
    table.play_card(user, card)
    return render_table(table)


def render_table(table):
    rendered_page = render_template('index.html', table=table)
    return make_response(rendered_page)


def render_create_table():
    user_name = request.cookies.get(COOKIE_USER_NAME)
    rendered_page = render_template('create_table.html', user_name="" if user_name is None else user_name)
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
    table_identifier = request.cookies.get(COOKIE_TABLE)
    if table_identifier is None:
        return None
    else:
        return tables.get(table_identifier)


def load_user():
    user_identifier = request.cookies.get(COOKIE_USER)
    if user_identifier is None:
        return None
    else:
        return users.get(user_identifier)


def set_cookie(response, cookie, value, max_age=None):
    response.set_cookie(cookie, value, samesite='Strict', httponly=True, max_age=max_age)


# Aufwärmanfragen der App Engine annehmen und positiv beantworten, damit immer eine aktive Instanz vorhanden ist
@app.route('/_ah/warmup')
def warmup():
    return '', 200, {}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
