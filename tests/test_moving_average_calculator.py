import unittest
from unittest.mock import patch

import pandas as pd

from src.analytics.indicators.moving_average_calculator import MovingAverageCalculator
from tests.fixtures import make_series


class MovingAverageCalculatorTests(unittest.TestCase):
    def test_short_history_returns_empty(self):
        calculator = MovingAverageCalculator(make_series(5))
        self.assertEqual(calculator.sma(20), [])
        self.assertIsNone(calculator.latest_sma(20).sma)

    def test_sma_maps_provider_values(self):
        values = pd.Series([None, 100.5, 101.5])
        with patch("src.analytics.indicators.moving_average_calculator.ta.sma", return_value=values):
            result = MovingAverageCalculator(make_series(3)).sma(2)
        self.assertIsNone(result[0].sma)
        self.assertEqual(result[-1].sma, 101.5)


if __name__ == "__main__":
    unittest.main()
