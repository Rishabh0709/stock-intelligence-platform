import unittest
from unittest.mock import patch

from src.analytics.indicators.macd_calculator import MACDCalculator
from tests.fixtures import make_series


class MACDCalculatorTests(unittest.TestCase):
    def test_provider_none_returns_no_signal(self):
        with patch("src.analytics.indicators.macd_calculator.ta.macd", return_value=None):
            calculator = MACDCalculator(make_series(40))
            self.assertEqual(calculator.macd(), [])
            self.assertIsNone(calculator.latest())


if __name__ == "__main__":
    unittest.main()
