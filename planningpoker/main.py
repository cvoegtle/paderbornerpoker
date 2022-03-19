from flask import Flask, request, render_template, make_response

from poker import Table, User

app = Flask(__name__)
user = User("Christian")
table = Table(user)

@app.route('/', methods=['GET', 'POST'])
def show_table():
    return render_table(table)

@app.route('/clear', methods=['POST'])
def clear_table():
    table.clear()
    return render_table(table)

@app.route('/show', methods=['POST'])
def show_cards_on_table():
    table.show_cards()
    return render_table(table)

@app.route('/card/<int:card_key>', methods=['POST'])
def start(card_key):
    card = table.cards[card_key]
    table.play_card(user, card)
    return render_table(table)



def render_table(table):
    rendered_page = render_template('index.html', table=table)
    response = make_response(rendered_page)
    return response

# Aufwärmanfragen der App Engine annehmen und positiv beantworten, damit immer eine aktive Instanz vorhanden ist
@app.route('/_ah/warmup')
def warmup():
    return '', 200, {}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
