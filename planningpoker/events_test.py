import unittest
import queue
import time
from unittest.mock import patch
from main import app
from poker import User, Table
from broadcaster import broadcaster


class TableEventsTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_events_without_table_id_returns_404(self):
        response = self.client.get('/table/events')
        self.assertEqual(404, response.status_code)

    def test_events_stream_headers(self):
        broadcaster.set_last_update(999, 12345)
        response = self.client.get('/table/events?table_id=999')
        self.assertEqual(200, response.status_code)
        self.assertEqual('text/event-stream; charset=utf-8', response.content_type)
        self.assertIn('no-cache', response.headers.get('Cache-Control', ''))
        self.assertEqual('no', response.headers.get('X-Accel-Buffering'))

    def test_events_stream_receives_notification(self):
        broadcaster.set_last_update(888, 1000)
        
        # Test generator directly
        with app.test_request_context('/table/events?table_id=888'):
            from main import table_events
            response = table_events()
            gen = response.response
            
            # Initial event should have the last_update
            first_chunk = next(gen)
            self.assertEqual("data: 1000\n\n", first_chunk)
            
            # Notify an update
            broadcaster.notify(888, 2000)
            second_chunk = next(gen)
            self.assertEqual("data: 2000\n\n", second_chunk)

    def test_events_stream_with_malformed_query_string(self):
        broadcaster.set_last_update(59, 12345)
        # Even with duplicate question mark from uniqueUrl
        response = self.client.get('/table/events?table_id=59?unique=1791054157890')
        self.assertEqual(200, response.status_code)
        self.assertEqual('text/event-stream; charset=utf-8', response.content_type)


class ValidationTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_validate_card_invalid_key_aborts_400(self):
        from main import validate_card
        with app.test_request_context():
            from werkzeug.exceptions import BadRequest
            with self.assertRaises(BadRequest):
                validate_card(14)

    def test_validate_card_valid_key_passes(self):
        from main import validate_card
        with app.test_request_context():
            # Should not raise exception
            validate_card(0)
            validate_card(12)

    def test_load_user_mandatory_missing_user_aborts(self):
        from main import load_user_mandatory
        with app.test_request_context():
            from werkzeug.exceptions import BadRequest
            with self.assertRaises(BadRequest):
                load_user_mandatory(400)

    def test_load_table_mandatory_missing_table_aborts(self):
        from main import load_table_mandatory
        with app.test_request_context():
            from werkzeug.exceptions import NotFound
            with self.assertRaises(NotFound):
                load_table_mandatory(404)

    def test_extract_table_identifier_mandatory_missing_aborts(self):
        from main import extract_table_identifier_mandatory
        with app.test_request_context():
            from werkzeug.exceptions import BadRequest
            with self.assertRaises(BadRequest):
                extract_table_identifier_mandatory(400)

    def test_extract_table_identifier_mandatory_present(self):
        from main import extract_table_identifier_mandatory
        with app.test_request_context(headers=[('Cookie', 'POKER_TABLE=789')]):
            self.assertEqual(789, extract_table_identifier_mandatory(400))

    @patch('main.update_table_play_card')
    def test_play_card_invalid_key_returns_400(self, mock_update):
        self.client.set_cookie('POKER_TABLE', '123')
        self.client.set_cookie('POKER_USER_ID', '456')
        response = self.client.post('/card/14')
        self.assertEqual(400, response.status_code)
        mock_update.assert_not_called()

    @patch('main.update_table_play_card')
    def test_play_card_missing_user_returns_400(self, mock_update):
        self.client.set_cookie('POKER_TABLE', '123')
        response = self.client.post('/card/3')
        self.assertEqual(400, response.status_code)
        mock_update.assert_not_called()

    @patch('main.update_table_play_card')
    def test_play_card_valid_request(self, mock_update):
        self.client.set_cookie('POKER_TABLE', '123')
        self.client.set_cookie('POKER_USER_ID', '456')
        user = User("Test")
        table = Table(user)
        table.identifier = 123
        with patch('main.load_user', return_value=user), patch('main.load_table', return_value=table):
            response = self.client.post('/card/3')
            self.assertEqual(302, response.status_code)
            self.assertIn('/table?unique=', response.headers.get('Location'))
            mock_update.assert_called_once_with(123, user, 3)


if __name__ == '__main__':
    unittest.main()
