import threading
import unittest
from cache import SafeCache


class TestSafeCache(unittest.TestCase):
    def test_get_or_set_does_not_deadlock(self):
        c = SafeCache()
        result = {}

        def worker():
            result["val"] = c.get_or_set("k1", lambda: 42)

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        t.join(timeout=0.5)
        self.assertFalse(t.is_alive(), "Deadlock detected in SafeCache.get_or_set")
        self.assertEqual(result.get("val"), 42)
        self.assertEqual(c.get("k1"), 42)

    def test_get_or_set_caches_value(self):
        c = SafeCache()
        calls = {"n": 0}

        def factory():
            calls["n"] += 1
            return "cached"

        t = threading.Thread(target=lambda: c.get_or_set("x", factory), daemon=True)
        t.start()
        t.join(timeout=0.5)
        self.assertFalse(t.is_alive(), "Deadlock detected in SafeCache.get_or_set")
        self.assertEqual(c.get_or_set("x", factory), "cached")
        self.assertEqual(calls["n"], 1)


if __name__ == "__main__":
    unittest.main()
