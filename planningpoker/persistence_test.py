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
        user = User("User Name", is_admin=True)
        table = Table(user, description="Paderborner Tisch")
        table.play_card(user, Card(2, value=3))
        json_table = json.dumps(table, cls=TableEncoder)
        table2 = json.JSONDecoder(object_hook=decode_json_table).decode(json_table)
        self.assertEqual(table.identifier, table2.identifier)
        card = table2.card_played_by(user)
        self.assertIsNotNone(card)
        self.assertEquals(1, len(table2.users))



if __name__ == '__main__':
    unittest.main()
