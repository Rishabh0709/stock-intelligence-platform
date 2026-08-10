import unittest

from src.analytics.indicators.adx_calculator import ADXCalculator
from tests.fixtures import make_series


class ADXCalculatorTests(unittest.TestCase):
    def test_short_history_returns_no_signal(self):
        calculator = ADXCalculator(make_series(10))
        self.assertEqual(calculator.adx(period=14), [])
        self.assertIsNone(calculator.latest(period=14))

    def test_invalid_period_is_rejected(self):
        with self.assertRaises(ValueError):
            ADXCalculator(make_series()).adx(0)


if __name__ == "__main__":
    unittest.main()
