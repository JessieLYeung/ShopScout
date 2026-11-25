from collections import OrderedDict
from copy import deepcopy
from threading import RLock
from time import monotonic


class TTLCache:
    def __init__(self, max_entries=256):
        self.max_entries = max_entries
        self._entries = OrderedDict()
        self._lock = RLock()

    def get(self, key):
        now = monotonic()
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None

            expires_at, value = entry
            if expires_at <= now:
                del self._entries[key]
                return None

            self._entries.move_to_end(key)
            return deepcopy(value)

    def set(self, key, value, ttl_seconds):
        if ttl_seconds <= 0:
            return

        with self._lock:
            self._entries[key] = (
                monotonic() + ttl_seconds,
                deepcopy(value),
            )
            self._entries.move_to_end(key)

            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
