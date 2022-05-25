import unittest
import poker

TEST_USER_NAME = "user"


class PokerTestCase(unittest.TestCase):
    def test_deck_building(self):
        deck = poker.build_deck([None])
        self.assertEqual(1, len(deck))
        self.assertEquals('?', deck[0].text)

    def test_standard_deck(self):
        deck = poker.standard_deck()
        print(deck)
        self.assertEqual(13, len(deck))

    def test_initial_table(self):
        admin = poker.User("Admin user")
        table = poker.Table(admin)
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
        self.assertEquals(2, table.average_card_value())
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
        admin = poker.User("Admin user")
        table = poker.Table(admin)
        table.play_card(admin, poker.Card(1, 1))
        self.assertFalse(table.is_users_card(admin, poker.Card(2,2)))
        self.assertTrue(table.is_users_card(admin, poker.Card(1,1)))

    def test_matching_cards(self):
        admin = poker.User("Admin user")
        table = poker.Table(admin)
        table.play_card(admin, poker.Card(1, 1))
        table.play_card(poker.User(TEST_USER_NAME), poker.Card(1, 1))

        self.assertFalse(table.matching_cards())
        self.assertFalse(table.differing_cards())
        table.show_cards()
        self.assertTrue(table.matching_cards())
        self.assertFalse(table.differing_cards())

    def test_match_null_value(self):
        admin = poker.User("Admin user")
        table = poker.Table(admin)
        table.play_card(admin, poker.Card(1, 1))
        table.play_card(poker.User(TEST_USER_NAME), poker.Card(2))
        self.assertFalse(table.differing_cards())
        table.show_cards()
        self.assertFalse(table.matching_cards())
        self.assertTrue(table.differing_cards())


if __name__ == '__main__':
    unittest.main()
