import unittest
from metrics import gross_margin


class TestMetrics(unittest.TestCase):
    def test_zero_revenue_returns_zero(self):
        self.assertEqual(gross_margin(0, 50), 0)

    def test_normal_margin(self):
        self.assertAlmostEqual(gross_margin(200.0, 50.0), 0.75)


if __name__ == "__main__":
    unittest.main()
