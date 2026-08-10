import unittest

from tests.fixtures import make_prices
from src.analytics.core.price_series import PriceSeries


class PriceSeriesTests(unittest.TestCase):
    def test_sorts_prices_and_exposes_latest_values(self):
        prices = list(reversed(make_prices(3)))
        series = PriceSeries(prices)
        self.assertEqual(series.count(), 3)
        self.assertLess(series.first().price_date, series.latest().price_date)
        self.assertEqual(series.latest_close(), 102)

    def test_empty_series_is_safe(self):
        series = PriceSeries([])
        self.assertTrue(series.is_empty())
        self.assertIsNone(series.latest())
        self.assertIsNone(series.latest_close())


if __name__ == "__main__":
    unittest.main()
