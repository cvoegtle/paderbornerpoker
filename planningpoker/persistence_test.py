import unittest
import json

from persistence import UserEncoder, decode_json_user, TableEncoder, decode_json_table
from poker import User, Table, Card


class JSONSerialisationTest(unittest.TestCase):
    def test_user_serialisation(self):
        user = User("User Name", is_admin=True)
        json_user = json.dumps(user, cls=UserEncoder)
        user2 = json.JSONDecoder(object_hook=decode_json_user).decode(json_user)
        self.assertEqual(user.name, user2.name)
        self.assertEqual(user.is_admin, user2.is_admin)
        self.assertEqual(user.identifier, user2.identifier)

    def test_table_serialisation(self):
        admin = User("Admin Name", is_admin=True)
        table = Table(admin, description="Paderborner Tisch")
        user = User("User name")
        table.add_user(user)
        table.play_card(admin, Card(2, value=3))
        table.play_card(user, Card(3, value=5))
        table.show_cards()
        json_table = json.dumps(table, cls=TableEncoder)
        table2 = json.JSONDecoder(object_hook=decode_json_table).decode(json_table)
        self.assertEqual(table.identifier, table2.identifier)
        self.assertEqual(table.description, table2.description)
        card = table2.card_played_by(admin)
        self.assertIsNotNone(card)
        self.assertEquals(2, len(table2.users))

        self.assertTrue(table2.card_value_visible)
        self.assertEqual(table.last_update, table2.last_update)



if __name__ == '__main__':
    unittest.main()
