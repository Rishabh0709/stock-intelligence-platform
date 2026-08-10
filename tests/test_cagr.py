import unittest
from datetime import date

from src.analytics.core.cagr_calculator import CAGRCalculator
from src.analytics.core.price_series import PriceSeries
from src.models.daily_price import DailyPrice


def candle(day, close):
    return DailyPrice(1, day, close, close, close, close, close, 1000)


class CAGRCalculatorTests(unittest.TestCase):
    def test_one_year_growth(self):
        series = PriceSeries(
            [candle(date(2025, 1, 1), 100), candle(date(2026, 1, 1), 121)]
        )
        self.assertAlmostEqual(CAGRCalculator(series).calculate(), 0.21, places=3)

    def test_insufficient_history_returns_none(self):
        self.assertIsNone(CAGRCalculator(PriceSeries([])).calculate())


if __name__ == "__main__":
    unittest.main()
