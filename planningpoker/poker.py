import random
import time

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

    def __eq__(self, other):
        return isinstance(other, Card) and self.key == other.key

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

    def __eq__(self, other):
        return isinstance(other, User) and other.identifier == self.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __str__(self):
        return f'<identifier: {self.identifier} / name: {self.name} / is_admin = {self.is_admin}>'

    def key(self):
        return ("A" if self.is_admin else "Z") + self.name


class Table:

    def __init__(self, admin=None, description=None, cards=None):
        self.identifier = random.randrange(0, MAX_IDENTIFIER)
        self.card_value_visible = False
        self.last_update = time.time_ns()
        self.save_time = ""
        self.played_cards = {}
        self.users = set()
        self.cards = []

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

    def __str__(self):
        return f'<identifier: {self.identifier} / description: {self.description} / save_time = {self.save_time} / card_value_visible = {self.card_value_visible} / played_cards = {self.played_cards}> '

    def add_user(self, user):
        self.users.add(user)
        self.mark_update()

    def clear(self, user):
        if self.card_played_by(user):
            self.played_cards.clear()
        self.card_value_visible = False
        self.mark_update()

    def show_cards(self):
        self.card_value_visible = True
        self.mark_update()

    def matching_cards(self):
        if not self.card_value_visible:
            return False
        contains_none = any([card.value is None for card in self.played_cards.values()])
        if contains_none:
            return False
        reference_value = next(iter(self.played_cards.values())).value
        return all([card.value == reference_value for card in self.played_cards.values()])

    def differing_cards(self):
        if not self.card_value_visible:
            return False
        contains_none = any([card.value is None for card in self.played_cards.values()])
        if contains_none:
            return True
        min_value = min([card.value for card in self.played_cards.values()])
        max_value = max([card.value for card in self.played_cards.values()])
        return max_value > 0 and (max_value - min_value) > 2 and (max_value - min_value) / max_value >= 0.5

    def play_card(self, user, card):
        self.played_cards[user.identifier] = card
        self.mark_update()

    def card_played_by(self, user):
        return self.played_cards.get(user.identifier)

    def is_users_card(self, user, card):
        return self.card_played_by(user) == card

    def all_cards_played(self):
        return len(self.users) <= len(self.played_cards)

    def sorted_users(self):
        return sorted(self.users, key=User.key)

    def is_user_at_table(self, lookup):
        for user in self.users:
            if user.identifier == lookup.identifier:
                return True
        return False

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
