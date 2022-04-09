import time

from flask import Flask, request, render_template, make_response, redirect

from persistence import retrieve_user, retrieve_table, create_user, create_table, update_table_add_user, update_table_clear, \
    update_table_show_cards, update_table_play_card

COOKIE_TABLE = "POKER_TABLE"
COOKIE_TABLE_UPDATE = "TABLE_UPDATE"
COOKIE_USER = "POKER_USER_ID"
COOKIE_USER_NAME = "POKER_USER_NAME"
COOKIE_AUTO_UPDATE = "AUTO_UPDATE"

app = Flask(__name__)


# Einstiegspunkt. Tisch anzeigen falls vorhanden,
# sonst eine Seite anzeigen um den Tisch anzulegen
@app.route('/', methods=['GET'])
def start_new_table():
    response = render_create_table()
    clear_cookie(response, COOKIE_TABLE)
    clear_cookie(response, COOKIE_TABLE_UPDATE)
    clear_cookie(response, COOKIE_USER)
    return response


@app.route('/table', methods=['GET', 'POST'])
def show_table():
    table = load_table()
    if table is None:
        return unique_redirect('/')
    else:
        return render_table(table, load_user())


# Adminbenutzer und Tisch anlegen.
# Cookies setzen, damit wir sie wiederfinden
@app.route('/create_table', methods=['POST'])
def do_create_table():
    user = create_user(request.form.get('user_name'), is_admin=True)
    table = create_table(user, request.form.get('table_name'))
    response = render_invite(table)
    set_cookie(response, COOKIE_TABLE, table.identifier)
    set_cookie(response, COOKIE_USER, user.identifier)
    set_cookie(response, COOKIE_USER_NAME, user.name)
    return response


# Einladungslink rendern, über den man dem Tisch beitreten kann
@app.route('/invitation/<int:table_identifier>', methods=['GET'])
def receive_invitation(table_identifier):
    table = retrieve_table(table_identifier)
    response = render_invitation(table)
    set_cookie(response, COOKIE_TABLE, table.identifier)
    return response


# Einladung annehmen und dem Tisch beitreten
@app.route('/accept_invitation', methods=['POST'])
def accept_invitation():
    user = create_user(request.form.get('user_name'))
    update_table_add_user(extract_table_identifier(), user)
    response = unique_redirect('/table')
    set_cookie(response, COOKIE_USER, user.identifier)
    set_cookie(response, COOKIE_USER_NAME, user.name)
    return response


# Tisch beitreten, aber nur zuschauen
@app.route('/watch_table', methods=['POST'])
def watch_table():
    user = create_user(request.form.get('user_name'))
    response = unique_redirect('/table')
    set_cookie(response, COOKIE_USER, user.identifier)
    set_cookie(response, COOKIE_USER_NAME, user.name)
    return response


@app.route('/clear', methods=['POST'])
def clear_table():
    update_table_clear(extract_table_identifier())
    response = unique_redirect('/table')
    return response


@app.route('/show', methods=['POST'])
def show_cards_on_table():
    update_table_show_cards(extract_table_identifier())
    response = unique_redirect('/table')
    return response


@app.route('/card/<int:card_key>', methods=['GET', 'POST'])
def play_card(card_key):
    update_table_play_card(extract_table_identifier(), load_user(), card_key)
    response = unique_redirect('/table')
    return response


def render_table(table, user):
    auto_update = request.cookies.get(COOKIE_AUTO_UPDATE) == "ON"
    show_disabled = not table.all_cards_played() and not user.is_admin
    rendered_page = render_template('table.html', table=table, my_user=user, show_action_disabled=show_disabled, auto_update=auto_update)
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


def unique_redirect(url):
    return redirect(f'{url}?unique={time.time_ns()}')


def load_table():
    table_identifier = extract_table_identifier()
    if table_identifier is None:
        return None
    else:
        return retrieve_table(table_identifier)


def extract_table_identifier():
    table_cookie = request.cookies.get(COOKIE_TABLE)
    return table_cookie


def load_user():
    user_cookie = request.cookies.get(COOKIE_USER)
    if user_cookie is None:
        return None
    else:
        user_identifier = int(user_cookie)
        return retrieve_user(user_identifier)


def set_cookie(response, cookie, value, max_age=None):
    response.set_cookie(cookie, str(value), samesite='Strict', httponly=False, max_age=max_age)


def clear_cookie(response, cookie):
    response.set_cookie(cookie, "", samesite='Strict', httponly=False, max_age=0)


# AJAX Anfrage, ob sich etwas am Tisch geändert hat
@app.route('/check_for_updates', methods=['GET', 'POST'])
def check_for_update():
    table = load_table()
    return str(table.last_update)


# Aufwärmanfragen der App Engine annehmen und positiv beantworten, damit immer eine aktive Instanz vorhanden ist
@app.route('/_ah/warmup')
def warmup():
    return '', 200, {}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
