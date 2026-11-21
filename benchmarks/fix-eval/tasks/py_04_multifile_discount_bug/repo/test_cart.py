import unittest
from cart import checkout_total


class TestCart(unittest.TestCase):
    def test_discount_and_tax(self):
        # 2 * 50.0 = 100.0 -> 10% off = 90.0 -> +10% tax = 99.0
        self.assertEqual(checkout_total([(50.0, 2)], discount_pct=10.0, tax_pct=10.0), 99.0)

    def test_zero_discount(self):
        self.assertEqual(checkout_total([(19.99, 2)], discount_pct=0.0, tax_pct=0.0), 39.98)


if __name__ == "__main__":
    unittest.main()
