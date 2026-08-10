import unittest

from src.analytics.statistics.volatility_calculator import VolatilityCalculator
from tests.fixtures import make_series


class VolatilityCalculatorTests(unittest.TestCase):
    def test_history_and_latest(self):
        calculator = VolatilityCalculator(make_series(10))
        history = calculator.history(period=3, annualize=False)
        self.assertTrue(history)
        self.assertEqual(calculator.latest(period=3, annualize=False), history[-1])

    def test_insufficient_history(self):
        self.assertIsNone(VolatilityCalculator(make_series(2)).latest(period=3))


if __name__ == "__main__":
    unittest.main()
