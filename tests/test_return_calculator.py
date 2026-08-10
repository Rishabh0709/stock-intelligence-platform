import unittest

from src.analytics.core.return_calculator import ReturnCalculator
from tests.fixtures import make_series


class ReturnCalculatorTests(unittest.TestCase):
    def test_returns_are_calculated_from_available_prices(self):
        calculator = ReturnCalculator(make_series(3))
        self.assertAlmostEqual(calculator.daily_return(), 1 / 101)
        self.assertAlmostEqual(calculator.total_return(), 0.02)

    def test_single_price_has_no_return(self):
        calculator = ReturnCalculator(make_series(1))
        self.assertIsNone(calculator.daily_return())
        self.assertIsNone(calculator.total_return())


if __name__ == "__main__":
    unittest.main()
