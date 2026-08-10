from __future__ import annotations

import pandas as pd

from src.screening.models import Signal
from src.screening.schema import latest_number, normalize_indicator_frame, require_columns


def detect_rsi_divergence(df: pd.DataFrame, window: int = 14) -> tuple[Signal, ...]:
    if window < 6:
        raise ValueError("Divergence window must be at least 6 bars")
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Close", "RSI_14"))
    recent = frame[["Close", "RSI_14"]].dropna().tail(window)
    bullish = bearish = False
    values: dict[str, float | int | str | bool | None] = {"window": window}
    if len(recent) >= window:
        split = len(recent) // 2
        first = recent.iloc[:split]
        second = recent.iloc[split:]
        first_low_idx = first["Close"].idxmin()
        second_low_idx = second["Close"].idxmin()
        first_high_idx = first["Close"].idxmax()
        second_high_idx = second["Close"].idxmax()
        first_low = float(frame.loc[first_low_idx, "Close"])
        second_low = float(frame.loc[second_low_idx, "Close"])
        first_low_rsi = float(frame.loc[first_low_idx, "RSI_14"])
        second_low_rsi = float(frame.loc[second_low_idx, "RSI_14"])
        first_high = float(frame.loc[first_high_idx, "Close"])
        second_high = float(frame.loc[second_high_idx, "Close"])
        first_high_rsi = float(frame.loc[first_high_idx, "RSI_14"])
        second_high_rsi = float(frame.loc[second_high_idx, "RSI_14"])
        bullish = second_low < first_low and second_low_rsi > first_low_rsi
        bearish = second_high > first_high and second_high_rsi < first_high_rsi
        values.update(
            {
                "first_price_low": first_low,
                "second_price_low": second_low,
                "first_low_rsi": first_low_rsi,
                "second_low_rsi": second_low_rsi,
                "first_price_high": first_high,
                "second_price_high": second_high,
                "first_high_rsi": first_high_rsi,
                "second_high_rsi": second_high_rsi,
            }
        )
    return (
        Signal(
            "bullish_rsi_divergence",
            "Bullish RSI Divergence",
            bullish,
            "bullish",
            "The second-half price low is lower while RSI at that low is higher.",
            values,
        ),
        Signal(
            "bearish_rsi_divergence",
            "Bearish RSI Divergence",
            bearish,
            "bearish",
            "The second-half price high is higher while RSI at that high is lower.",
            values,
        ),
    )


def detect_macd_signals(df: pd.DataFrame, near_zero_fraction: float = 0.15) -> tuple[Signal, ...]:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("MACD", "MACD_Signal", "MACD_Histogram"))
    macd = frame["MACD"].dropna()
    signal = frame["MACD_Signal"].dropna()
    aligned = frame[["MACD", "MACD_Signal"]].dropna()
    zero_rebound = False
    tolerance = None
    if len(aligned) >= 3:
        scale = float(aligned["MACD"].abs().tail(20).max())
        tolerance = max(scale * near_zero_fraction, 1e-9)
        previously_above_zero = bool((aligned["MACD"].iloc[-6:-2] > 0).any())
        zero_rebound = bool(
            previously_above_zero
            and aligned.iloc[-1]["MACD"] > 0
            and abs(aligned.iloc[-2]["MACD"]) <= tolerance
            and aligned.iloc[-2]["MACD"] <= aligned.iloc[-2]["MACD_Signal"]
            and aligned.iloc[-1]["MACD"] > aligned.iloc[-1]["MACD_Signal"]
        )
    histogram = frame["MACD_Histogram"].dropna().tail(3)
    acceleration = bool(
        len(histogram) == 3
        and (histogram > 0).all()
        and histogram.is_monotonic_increasing
        and histogram.nunique() == 3
    )
    values = {
        "macd": float(macd.iloc[-1]) if not macd.empty else None,
        "signal": float(signal.iloc[-1]) if not signal.empty else None,
        "histogram": float(histogram.iloc[-1]) if not histogram.empty else None,
        "near_zero_tolerance": tolerance,
    }
    return (
        Signal(
            "macd_zero_line_rebound",
            "MACD Zero-Line Rebound",
            zero_rebound,
            "bullish",
            "MACD rebounded near zero and crossed back above its signal line.",
            values,
        ),
        Signal(
            "macd_histogram_acceleration",
            "MACD Histogram Acceleration",
            acceleration,
            "bullish",
            "MACD histogram is positive and increased for three consecutive bars.",
            values,
        ),
    )


def detect_rsi_oversold_rebound(df: pd.DataFrame) -> Signal:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Close", "SMA_200", "RSI_14"))
    recent = frame[["Close", "SMA_200", "RSI_14"]].dropna()
    active = bool(
        len(recent) >= 2
        and recent.iloc[-2]["RSI_14"] < 30
        and recent.iloc[-1]["RSI_14"] > recent.iloc[-2]["RSI_14"]
        and recent.iloc[-1]["Close"] > recent.iloc[-1]["SMA_200"]
    )
    return Signal(
        "rsi_oversold_rebound",
        "RSI Oversold Rebound",
        active,
        "bullish",
        "RSI turned upward from below 30 while price remained above SMA 200.",
        {
            "price": latest_number(frame, "Close"),
            "sma_200": latest_number(frame, "SMA_200"),
            "rsi": latest_number(frame, "RSI_14"),
        },
    )


def momentum_signals(df: pd.DataFrame) -> tuple[Signal, ...]:
    return (
        *detect_rsi_divergence(df),
        *detect_macd_signals(df),
        detect_rsi_oversold_rebound(df),
    )
