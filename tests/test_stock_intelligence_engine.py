from __future__ import annotations

import numpy as np
import pandas as pd
import unittest

from src.screening.engine import analyze_stock, scan_stocks
from src.screening.momentum_engine import detect_macd_signals, detect_rsi_divergence
from src.screening.risk_engine import (
    calculate_position_size,
    calculate_risk_metrics,
    find_nearest_resistance,
)
from src.screening.scoring_engine import calculate_stock_score
from src.screening.schema import build_indicator_frame
from src.screening.trend_engine import detect_macro_cross
from src.screening.volatility_engine import (
    detect_band_touch_reversal,
    detect_bollinger_squeeze,
)
from src.screening.volume_engine import (
    detect_institutional_volume,
    detect_obv_leading_breakout,
    detect_vwap_bias,
)


def make_frame(rows: int = 260) -> pd.DataFrame:
    x = np.arange(rows, dtype=float)
    close = 100 + x * 0.25
    volume = np.full(rows, 1000.0)
    frame = pd.DataFrame(
        {
            "Date": pd.date_range("2025-01-01", periods=rows, freq="D"),
            "Open": close - 0.5,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": volume,
            "SMA_20": close - 1.0,
            "SMA_50": close - 3.0,
            "SMA_200": close - 10.0,
            "EMA_20": close - 1.0,
            "EMA_50": close - 4.0,
            "ATR_14": np.full(rows, 2.0),
            "MACD": np.full(rows, 2.0),
            "MACD_Signal": np.full(rows, 1.0),
            "MACD_Histogram": np.full(rows, 1.0),
            "RSI_14": np.full(rows, 58.0),
            "BB_Upper": close + 3.0,
            "BB_Middle": close,
            "BB_Lower": close - 3.0,
            "ADX_14": np.full(rows, 30.0),
            "Plus_DI_14": np.full(rows, 28.0),
            "Minus_DI_14": np.full(rows, 14.0),
            "OBV": x * 1000,
            "VWAP_Daily": close - 0.5,
            "VWAP_Weekly": close - 1.0,
        }
    )
    frame.loc[rows - 1, "Volume"] = 2000
    return frame


class StockIntelligenceEngineTests(unittest.TestCase):
    def test_macro_cross_is_a_latest_bar_event(self) -> None:
        frame = make_frame()
        frame.loc[frame.index[-2], ["SMA_50", "SMA_200"]] = [149.0, 150.0]
        frame.loc[frame.index[-1], ["SMA_50", "SMA_200"]] = [151.0, 150.0]
        signals = {signal.key: signal for signal in detect_macro_cross(frame)}
        self.assertTrue(signals["golden_cross"].active)
        self.assertFalse(signals["death_cross"].active)

    def test_score_uses_exact_100_point_weighting(self) -> None:
        result = calculate_stock_score(make_frame())
        self.assertEqual(result.max_score, 100)
        self.assertEqual(result.score, 80)
        self.assertEqual(
            result.category,
            "High Conviction Buy / Breakout Candidate",
        )

    def test_position_size_and_risk_reward_gate(self) -> None:
        self.assertEqual(calculate_position_size(100_000, 1, 10), 50)
        risk = calculate_risk_metrics(
            entry_price=100,
            atr=5,
            account_capital=100_000,
            risk_percent=1,
            resistance=130,
            highest_price_since_entry=110,
        )
        self.assertEqual(risk.initial_stop, 90)
        self.assertEqual(risk.trailing_stop, 97.5)
        self.assertEqual(risk.risk_reward_ratio, 3.0)
        self.assertTrue(risk.eligible)

    def test_scanner_filters_low_rrr_setups(self) -> None:
        candidates = scan_stocks(
            {"good": make_frame(), "weak": make_frame()},
            account_capital=100_000,
            resistance_by_symbol={"GOOD": 180.0, "WEAK": 166.0},
        )
        self.assertEqual(
            [candidate.symbol for candidate in candidates],
            ["GOOD"],
        )

    def test_full_analysis_returns_explainable_signals(self) -> None:
        report = analyze_stock(
            make_frame(),
            symbol="reliance",
            account_capital=500_000,
            resistance=190,
        )
        self.assertEqual(report.symbol, "RELIANCE")
        self.assertGreaterEqual(report.score.score, 60)
        self.assertEqual(len(report.signals), 20)
        self.assertTrue(all(signal.explanation for signal in report.signals))

    def test_invalid_risk_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "risk_percent"):
            calculate_position_size(100_000, 0, 5)

    def test_builder_attaches_raw_indicator_outputs(self) -> None:
        source = make_frame(30)
        price_columns = source[["Date", "Open", "High", "Low", "Close", "Volume"]]
        result = build_indicator_frame(
            price_columns,
            {"sma50": source["SMA_50"], "MACDh_12_26_9": source["MACD_Histogram"]},
        )
        self.assertIn("SMA_50", result.columns)
        self.assertIn("MACD_Histogram", result.columns)

    def test_builder_rejects_misaligned_indicator_history(self) -> None:
        source = make_frame(30)
        with self.assertRaisesRegex(ValueError, "expected 30"):
            build_indicator_frame(source, {"RSI_14": [50.0] * 29})

    def test_bullish_rsi_divergence_compares_two_swing_windows(self) -> None:
        frame = make_frame(20)
        frame.loc[6:19, "Close"] = [100, 95, 90, 96, 99, 98, 94, 85, 95, 97, 98, 99, 100, 101]
        frame.loc[6:19, "RSI_14"] = [50, 40, 22, 38, 45, 43, 39, 31, 40, 44, 47, 49, 51, 53]
        signals = {signal.key: signal for signal in detect_rsi_divergence(frame)}
        self.assertTrue(signals["bullish_rsi_divergence"].active)
        self.assertFalse(signals["bearish_rsi_divergence"].active)

    def test_macd_zero_rebound_and_histogram_acceleration(self) -> None:
        frame = make_frame(30)
        frame.loc[frame.index[-4:], "MACD"] = [1.0, 0.4, 0.05, 0.2]
        frame.loc[frame.index[-4:], "MACD_Signal"] = [0.8, 0.3, 0.1, 0.1]
        frame.loc[frame.index[-3:], "MACD_Histogram"] = [0.02, 0.05, 0.1]
        signals = {signal.key: signal for signal in detect_macd_signals(frame)}
        self.assertTrue(signals["macd_zero_line_rebound"].active)
        self.assertTrue(signals["macd_histogram_acceleration"].active)

    def test_squeeze_and_lower_band_reversal(self) -> None:
        frame = make_frame(30)
        frame.loc[:, "ATR_14"] = 3.0
        frame.loc[:, "BB_Upper"] = frame["EMA_20"] + 2.0
        frame.loc[:, "BB_Lower"] = frame["EMA_20"] - 2.0
        self.assertTrue(detect_bollinger_squeeze(frame)[0].active)
        frame.loc[frame.index[-2], "Close"] = frame.loc[frame.index[-2], "BB_Lower"] - 1
        frame.loc[frame.index[-1], "Close"] = frame.loc[frame.index[-1], "BB_Lower"] + 1
        self.assertTrue(detect_band_touch_reversal(frame).active)

    def test_institutional_volume_obv_and_vwap_signals(self) -> None:
        frame = make_frame(30)
        frame.loc[:, "Close"] = 100.0
        frame.loc[:, "Open"] = 99.0
        frame.loc[:, "VWAP_Daily"] = 98.0
        frame.loc[:, "VWAP_Weekly"] = 97.0
        frame.loc[:, "Volume"] = 1000.0
        frame.loc[frame.index[-1], "Volume"] = 3000.0
        frame.loc[:, "OBV"] = 1000.0
        frame.loc[frame.index[-1], "OBV"] = 2000.0
        self.assertTrue(detect_institutional_volume(frame).active)
        self.assertTrue(detect_obv_leading_breakout(frame).active)
        self.assertTrue(detect_vwap_bias(frame).active)

    def test_nearest_resistance_prefers_closest_confirmed_pivot(self) -> None:
        frame = make_frame(80)
        frame.loc[:, "Close"] = 100.0
        frame.loc[:, "High"] = 101.0
        frame.loc[30, "High"] = 120.0
        frame.loc[60, "High"] = 110.0
        self.assertEqual(find_nearest_resistance(frame), 110.0)


if __name__ == "__main__":
    unittest.main()
