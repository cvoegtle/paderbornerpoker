import random, time

MAX_IDENTIFIER = 100000000


class Card:
    def __init__(self, key, value=None, text=None):
        self.key = key
        self.value = value
        if text != None:
            self.text = text
        elif value == None:
            self.text = '?'
        else:
            self.text = str(value)

    def __str__(self):
        return f'<text: {self.text} / value: {self.value}>'

    def __repr__(self):
        return str(self)


def build_deck(values):
    cards = {key: Card(key, value) for key, value in enumerate(values)}
    return cards


def standard_deck():
    return build_deck([0, 0.5, 1, 2, 3, 5, 8, 13, 20, 40, 80, 100, None])


class User:
    def __init__(self, name="", is_admin=False):
        self.identifier = random.randrange(0, MAX_IDENTIFIER)
        self.name = name
        self.is_admin = is_admin


class Table:
    identifier = random.randrange(0, MAX_IDENTIFIER)
    users = set()
    cards = []
    played_cards = {}
    card_value_visible = False
    last_update = time.time_ns()

    def __init__(self, admin=None, description=None, cards=None):
        if description:
            self.description = description
        else:
            self.description = f'Tisch {self.identifier}'

        if cards is None:
            cards = standard_deck()
        self.cards = cards

        if admin is not None:
            admin.is_admin = True
            self.users.add(admin)

    def add_user(self, user):
        self.users.add(user)
        self.mark_update()

    def clear(self):
        self.played_cards.clear()
        self.card_value_visible = False
        self.mark_update()

    def show_cards(self):
        self.card_value_visible = True
        self.mark_update()

    def play_card(self, user, card):
        self.played_cards[user] = card
        self.mark_update()

    def remove_card(self, user):
        del self.played_cards[user]
        self.mark_update()

    def all_cards_played(self):
        return len(self.users) == len(self.played_cards)

    def average_card_value(self):
        average_value = 0
        number_of_valid_cards = 0
        for user, card in self.played_cards.items():
            if card.value is not None:
                average_value += card.value
                number_of_valid_cards += 1

        return None if number_of_valid_cards == 0 else average_value / number_of_valid_cards

    def mark_update(self):
        self.last_update = time.time_ns()


