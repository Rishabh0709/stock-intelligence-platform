import sys
import unittest
from types import ModuleType
from unittest.mock import patch

import pandas as pd


def fake_bbands(close, length=20, std=2.0):
    middle = close.rolling(length).mean()
    deviation = close.rolling(length).std(ddof=0)

    return pd.DataFrame(
        {
            f"BBL_{length}_{std}": middle - std * deviation,
            f"BBM_{length}_{std}": middle,
            f"BBU_{length}_{std}": middle + std * deviation,
        },
        index=close.index,
    )


fake_pandas_ta = ModuleType("pandas_ta")
fake_pandas_ta.bbands = fake_bbands
sys.modules.setdefault("pandas_ta", fake_pandas_ta)
sys.modules["pandas_ta"].bbands = fake_bbands

from src.analytics.indicators.bollinger_band_calculator import (
    BollingerBandCalculator,
)


class StubPriceSeries:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe


class BollingerBandCalculatorTests(unittest.TestCase):
    @staticmethod
    def calculator(closes) -> BollingerBandCalculator:
        dataframe = pd.DataFrame(
            {
                "Date": pd.date_range("2026-01-01", periods=len(closes)),
                "Close": closes,
            }
        )
        return BollingerBandCalculator(StubPriceSeries(dataframe))

    def test_rejects_invalid_parameters(self):
        calculator = self.calculator(range(25))

        with self.assertRaises(ValueError):
            calculator.bands(period=0)

        with self.assertRaises(ValueError):
            calculator.bands(std=0)

    def test_returns_empty_for_insufficient_history(self):
        self.assertEqual(self.calculator(range(19)).bands(), [])

    def test_returns_empty_when_indicator_library_returns_none(self):
        calculator = self.calculator(range(25))

        with patch(
            "src.analytics.indicators.bollinger_band_calculator.ta.bbands",
            return_value=None,
        ):
            self.assertEqual(calculator.bands(), [])
            self.assertIsNone(calculator.latest())

    def test_returns_empty_when_expected_columns_are_missing(self):
        calculator = self.calculator(range(25))

        with patch(
            "src.analytics.indicators.bollinger_band_calculator.ta.bbands",
            return_value=pd.DataFrame({"unexpected": range(25)}),
        ):
            self.assertEqual(calculator.bands(), [])

    def test_ignores_invalid_close_values(self):
        closes = list(range(25)) + [None, "invalid"]
        history = self.calculator(closes).bands()

        self.assertTrue(history)
        self.assertEqual(len(history), 25)

    def test_latest_returns_latest_complete_band(self):
        calculator = self.calculator(range(25))
        bands = fake_bbands(
            pd.Series(range(25), dtype="float64"),
            length=20,
            std=2.0,
        )
        bands.iloc[-1] = [None, None, None]

        with patch(
            "src.analytics.indicators.bollinger_band_calculator.ta.bbands",
            return_value=bands,
        ):
            latest = calculator.latest()

        self.assertIsNotNone(latest)
        self.assertEqual(latest.date.isoformat(), "2026-01-24")


if __name__ == "__main__":
    unittest.main()
