import unittest

from src.analytics.indicators.atr_calculator import ATRCalculator
from tests.fixtures import make_series


class ATRCalculatorTests(unittest.TestCase):
    def test_short_history_returns_no_signal(self):
        calculator = ATRCalculator(make_series(10))
        self.assertEqual(calculator.atr(period=14), [])
        self.assertIsNone(calculator.latest(period=14))

    def test_invalid_period_is_rejected(self):
        with self.assertRaises(ValueError):
            ATRCalculator(make_series()).atr(0)


if __name__ == "__main__":
    unittest.main()
