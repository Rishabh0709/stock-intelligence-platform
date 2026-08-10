from __future__ import annotations

import pandas as pd

from src.screening.models import Signal
from src.screening.schema import latest_number, normalize_indicator_frame, require_columns


def detect_institutional_volume(df: pd.DataFrame, multiplier: float = 2.5) -> Signal:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Open", "Close", "Volume"))
    volumes = frame["Volume"].dropna()
    reference = volumes.iloc[-21:-1] if len(volumes) >= 21 else pd.Series(dtype=float)
    average = float(reference.mean()) if len(reference) == 20 else None
    current_volume = latest_number(frame, "Volume")
    current_open = latest_number(frame, "Open")
    current_close = latest_number(frame, "Close")
    ratio = current_volume / average if average and current_volume is not None else None
    active = bool(
        ratio is not None
        and ratio > multiplier
        and current_close is not None
        and current_open is not None
        and current_close > current_open
    )
    return Signal(
        "institutional_volume_buying",
        "Institutional Volume Buying",
        active,
        "bullish",
        f"Bullish candle volume exceeded {multiplier}x its prior 20-bar average.",
        {
            "volume": current_volume,
            "volume_sma_20": average,
            "volume_ratio": round(ratio, 3) if ratio is not None else None,
        },
    )


def detect_obv_leading_breakout(df: pd.DataFrame, consolidation_pct: float = 8.0) -> Signal:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Close", "OBV"))
    recent = frame[["Close", "OBV"]].dropna().tail(21)
    active = False
    price_range_pct = None
    if len(recent) >= 21:
        prior = recent.iloc[:-1]
        price_mean = float(prior["Close"].mean())
        price_range_pct = (
            float(prior["Close"].max() - prior["Close"].min()) / price_mean * 100
            if price_mean
            else None
        )
        obv_breakout = recent.iloc[-1]["OBV"] > prior["OBV"].max()
        price_not_breakout = recent.iloc[-1]["Close"] <= prior["Close"].max()
        active = bool(
            price_range_pct is not None
            and price_range_pct <= consolidation_pct
            and obv_breakout
            and price_not_breakout
        )
    return Signal(
        "obv_leading_breakout",
        "OBV Leading Breakout",
        active,
        "bullish",
        "OBV reached a new 20-bar high while price remained inside a tight consolidation.",
        {
            "obv": latest_number(frame, "OBV"),
            "price_range_pct": round(price_range_pct, 3) if price_range_pct is not None else None,
            "consolidation_limit_pct": consolidation_pct,
        },
    )


def detect_vwap_bias(df: pd.DataFrame) -> Signal:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Close", "Volume", "VWAP_Daily", "VWAP_Weekly"))
    recent = frame[["Close", "Volume", "VWAP_Daily", "VWAP_Weekly"]].dropna()
    active = bool(
        len(recent) >= 2
        and recent.iloc[-1]["Close"] > recent.iloc[-1]["VWAP_Daily"]
        and recent.iloc[-1]["Close"] > recent.iloc[-1]["VWAP_Weekly"]
        and recent.iloc[-1]["Volume"] > recent.iloc[-2]["Volume"]
    )
    return Signal(
        "bullish_vwap_bias",
        "Bullish VWAP Bias",
        active,
        "bullish",
        "Price is above daily and weekly VWAP while volume is rising.",
        {
            "price": latest_number(frame, "Close"),
            "daily_vwap": latest_number(frame, "VWAP_Daily"),
            "weekly_vwap": latest_number(frame, "VWAP_Weekly"),
            "volume": latest_number(frame, "Volume"),
        },
    )


def volume_signals(df: pd.DataFrame) -> tuple[Signal, ...]:
    return (
        detect_institutional_volume(df),
        detect_obv_leading_breakout(df),
        detect_vwap_bias(df),
    )
