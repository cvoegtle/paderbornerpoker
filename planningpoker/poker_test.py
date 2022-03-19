import unittest
import poker


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

if __name__ == '__main__':
    unittest.main()
