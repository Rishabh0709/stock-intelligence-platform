import unittest
from datetime import date

from src.analytics.core.drawdown_calculator import DrawdownCalculator
from src.analytics.core.price_series import PriceSeries
from src.models.daily_price import DailyPrice


def candle(index, close):
    return DailyPrice(1, date(2026, 1, index), close, close, close, close, close, 1000)


class DrawdownCalculatorTests(unittest.TestCase):
    def test_maximum_drawdown(self):
        calculator = DrawdownCalculator(PriceSeries([candle(1, 100), candle(2, 80), candle(3, 90)]))
        self.assertAlmostEqual(calculator.maximum(), -0.20)
        self.assertAlmostEqual(calculator.latest(), -0.10)

    def test_empty_history(self):
        calculator = DrawdownCalculator(PriceSeries([]))
        self.assertIsNone(calculator.maximum())


if __name__ == "__main__":
    unittest.main()
