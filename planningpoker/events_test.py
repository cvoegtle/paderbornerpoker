import unittest
import queue
import time
from main import app
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


if __name__ == '__main__':
    unittest.main()
