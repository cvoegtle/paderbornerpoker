import unittest
import poker

TEST_USER_NAME = "user"


class PokerTestCase(unittest.TestCase):
    def test_deck_building(self):
        deck = poker.build_deck([None])
        self.assertEqual(1, len(deck))
        self.assertEqual('?', deck[0].text)

    def test_standard_deck(self):
        deck = poker.standard_deck()
        print(deck)
        self.assertEqual(13, len(deck))

    def test_initial_table(self):
        admin, table = create_admin_and_table()
        player = poker.User("First User")
        table.add_user(player)

        self.assertFalse(table.all_cards_played())
        self.assertIsNone(table.average_card_value())

        table.play_card(player, poker.Card(1, 1))
        table.play_card(player, poker.Card(2, 2))
        self.assertFalse(table.all_cards_played())
        self.assertEqual(1, len(table.played_cards))

        table.play_card(admin, poker.Card(3, 2))
        self.assertTrue(table.all_cards_played())
        self.assertEqual(2, table.average_card_value())
        print(table)

    def test_user_identity(self):
        user = poker.User(TEST_USER_NAME)
        card = poker.Card(1, 100)
        table = poker.Table(user)
        table.play_card(user, card)

        user2 = poker.User(TEST_USER_NAME)
        played_card = table.card_played_by(user2)
        self.assertNotEqual(card, played_card)

    def test_card_played_by(self):
        admin, table = create_admin_and_table()
        table.play_card(admin, poker.Card(1, 1))
        self.assertFalse(table.is_users_card(admin, poker.Card(2,2)))
        self.assertTrue(table.is_users_card(admin, poker.Card(1,1)))

    def test_matching_cards(self):
        admin, table = create_admin_and_table()
        table.play_card(admin, poker.Card(1, 1))
        table.play_card(poker.User(TEST_USER_NAME), poker.Card(1, 1))

        self.assertFalse(table.matching_cards())
        self.assertFalse(table.differing_cards())
        table.show_cards()
        self.assertTrue(table.matching_cards())
        self.assertFalse(table.differing_cards())

    def test_match_null_value(self):
        admin, table = create_admin_and_table()
        table.play_card(admin, poker.Card(1, 1))
        table.play_card(poker.User(TEST_USER_NAME), poker.Card(2))
        self.assertFalse(table.differing_cards())
        table.show_cards()
        self.assertFalse(table.matching_cards())
        self.assertTrue(table.differing_cards())

    def test_remove_user_from_table_with_card(self):
        admin, table = create_admin_and_table()
        user = poker.User("User")
        table.add_user(user)
        table.play_card(user, poker.Card(1))
        table.remove_user(user)

        self.assertEqual(1, len(table.users))
        self.assertIsNone(table.card_played_by(user))

    def test_remove_user_from_table(self):
        admin, table = create_admin_and_table()
        user = poker.User("User")
        table.add_user(user)
        table.remove_user(user)

        self.assertEqual(1, len(table.users))
        self.assertIsNone(table.card_played_by(user))

    def test_cannot_play_card_after_show(self):
        admin, table = create_admin_and_table()
        user = poker.User("User")
        table.add_user(user)
        card1 = poker.Card(1, 1)
        card2 = poker.Card(2, 2)

        table.play_card(admin, card1)
        table.show_cards()
        last_update_after_show = table.last_update

        table.play_card(admin, card2)
        table.play_card(user, card1)

        self.assertEqual(card1, table.card_played_by(admin))
        self.assertIsNone(table.card_played_by(user))
        self.assertEqual(last_update_after_show, table.last_update)

    def test_show_cards_without_played_cards(self):
        admin, table = create_admin_and_table()
        table.show_cards()
        self.assertFalse(table.card_value_visible)
        self.assertFalse(table.matching_cards())
        self.assertFalse(table.differing_cards())

        # Single card played (value or ?) should not trigger matching or differing animations
        table.play_card(admin, poker.Card(1, 1))
        table.show_cards()
        self.assertFalse(table.matching_cards())
        self.assertFalse(table.differing_cards())

        table.clear(admin)
        table.play_card(admin, poker.Card(12, None))
        table.show_cards()
        self.assertFalse(table.matching_cards())
        self.assertFalse(table.differing_cards())

        table.remove_user(admin)
        self.assertFalse(table.matching_cards())
        self.assertFalse(table.differing_cards())


def create_admin_and_table():
    admin = poker.User("Admin user")
    table = poker.Table(admin)
    return admin, table


if __name__ == '__main__':
    unittest.main()
