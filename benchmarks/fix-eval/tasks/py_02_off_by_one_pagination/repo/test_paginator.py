import unittest
from paginator import paginate


class TestPaginator(unittest.TestCase):
    def test_exact_page_size_returns_all_items(self):
        res = paginate([1, 2, 3, 4, 5], page=1, page_size=2)
        self.assertEqual(res["items"], [1, 2])
        self.assertEqual(res["total_pages"], 3)

    def test_last_partial_page(self):
        res = paginate([1, 2, 3, 4, 5], page=3, page_size=2)
        self.assertEqual(res["items"], [5])
        self.assertEqual(res["total_pages"], 3)

    def test_empty_items(self):
        res = paginate([], page=1, page_size=10)
        self.assertEqual(res["items"], [])
        self.assertEqual(res["total_pages"], 0)


if __name__ == "__main__":
    unittest.main()
