import queue
import threading
from collections import defaultdict


class Broadcaster:
    def __init__(self):
        self._listeners = defaultdict(set)
        self._last_updates = {}
        self._lock = threading.Lock()

    def subscribe(self, table_id):
        q = queue.Queue(maxsize=20)
        with self._lock:
            self._listeners[table_id].add(q)
        return q

    def unsubscribe(self, table_id, q):
        with self._lock:
            listeners = self._listeners.get(table_id)
            if listeners:
                listeners.discard(q)
                if not listeners:
                    del self._listeners[table_id]

    def notify(self, table_id, update_id):
        update_str = str(update_id)
        with self._lock:
            self._last_updates[table_id] = update_str
            listeners = list(self._listeners.get(table_id, []))

        for q in listeners:
            try:
                q.put_nowait(update_str)
            except queue.Full:
                try:
                    q.get_nowait()
                except queue.Empty:
                    pass
                try:
                    q.put_nowait(update_str)
                except queue.Full:
                    pass

    def get_last_update(self, table_id):
        with self._lock:
            return self._last_updates.get(table_id)

    def set_last_update(self, table_id, update_id):
        if not table_id:
            return
        with self._lock:
            self._last_updates[table_id] = str(update_id)


broadcaster = Broadcaster()
