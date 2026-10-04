import unittest
import queue
from broadcaster import Broadcaster


class BroadcasterTestCase(unittest.TestCase):
    def setUp(self):
        self.broadcaster = Broadcaster()

    def test_subscribe_and_notify(self):
        q = self.broadcaster.subscribe(100)
        self.broadcaster.notify(100, 12345)
        self.assertEqual("12345", q.get_nowait())

    def test_none_or_empty_table_id(self):
        self.assertIsNone(self.broadcaster.subscribe(None))
        self.assertIsNone(self.broadcaster.get_last_update(None))
        # notify and set_last_update with None should be safe no-ops
        self.broadcaster.notify(None, 123)
        self.broadcaster.set_last_update(None, 123)
        self.broadcaster.unsubscribe(None, None)

    def test_multiple_tables_isolation(self):
        q1 = self.broadcaster.subscribe(1)
        q2 = self.broadcaster.subscribe(2)
        self.broadcaster.notify(1, 999)

        self.assertEqual("999", q1.get_nowait())
        self.assertTrue(q2.empty())

    def test_unsubscribe(self):
        q = self.broadcaster.subscribe(1)
        self.broadcaster.unsubscribe(1, q)
        self.broadcaster.notify(1, 888)
        self.assertTrue(q.empty())
        self.assertNotIn(1, self.broadcaster._listeners)

    def test_get_and_set_last_update(self):
        self.broadcaster.set_last_update(42, 555)
        self.assertEqual("555", self.broadcaster.get_last_update(42))
        self.broadcaster.notify(42, 777)
        self.assertEqual("777", self.broadcaster.get_last_update(42))

    def test_queue_overflow_does_not_block(self):
        q = self.broadcaster.subscribe(5)
        for i in range(30):
            self.broadcaster.notify(5, i)
        # Queue maxsize is 20, latest items should be present
        self.assertEqual(20, q.qsize())


if __name__ == '__main__':
    unittest.main()
