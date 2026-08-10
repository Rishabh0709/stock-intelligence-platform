import unittest
from types import ModuleType
from unittest.mock import patch
import sys

import pandas as pd


def fake_rsi(close, length=14):
    values = [None] * len(close)

    if len(close) > length:
        values[length:] = [50.0] * (len(close) - length)

    return pd.Series(values, index=close.index, dtype="float64")


fake_pandas_ta = ModuleType("pandas_ta")
fake_pandas_ta.rsi = fake_rsi
sys.modules.setdefault("pandas_ta", fake_pandas_ta)
sys.modules["pandas_ta"].rsi = fake_rsi

from src.analytics.indicators.rsi_calculator import RSICalculator


class StubPriceSeries:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe


class RSICalculatorTests(unittest.TestCase):
    @staticmethod
    def calculator(closes) -> RSICalculator:
        dataframe = pd.DataFrame(
            {
                "Date": pd.date_range("2026-01-01", periods=len(closes)),
                "Close": closes,
            }
        )
        return RSICalculator(StubPriceSeries(dataframe))

    def test_rejects_non_positive_period(self):
        with self.assertRaises(ValueError):
            self.calculator([100, 101]).rsi(0)

    def test_returns_empty_for_insufficient_history(self):
        self.assertEqual(self.calculator(range(14)).rsi(14), [])

    def test_returns_empty_when_indicator_library_returns_none(self):
        calculator = self.calculator(range(20))

        with patch(
            "src.analytics.indicators.rsi_calculator.ta.rsi",
            return_value=None,
        ):
            self.assertEqual(calculator.rsi(), [])
            self.assertIsNone(calculator.latest())

    def test_ignores_invalid_close_values(self):
        closes = list(range(20)) + [None, "invalid"]
        history = self.calculator(closes).rsi()

        self.assertTrue(history)
        self.assertEqual(len(history), 20)

    def test_latest_returns_latest_non_null_rsi(self):
        calculator = self.calculator(range(20))
        values = pd.Series(
            [None] * 14 + [45.0, 48.0, 51.0, None, None, None]
        )

        with patch(
            "src.analytics.indicators.rsi_calculator.ta.rsi",
            return_value=values,
        ):
            self.assertEqual(calculator.latest(), 51.0)


if __name__ == "__main__":
    unittest.main()
