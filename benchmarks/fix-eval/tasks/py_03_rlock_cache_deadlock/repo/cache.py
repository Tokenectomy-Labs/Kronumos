import threading


class SafeCache:
    def __init__(self):
        self._lock = threading.Lock()
        self._store = {}

    def get(self, key):
        with self._lock:
            return self._store.get(key)

    def set(self, key, value):
        with self._lock:
            self._store[key] = value
            return value

    def get_or_set(self, key, factory):
        with self._lock:
            if key in self._store:
                return self._store[key]
            value = factory()
            return self.set(key, value)
