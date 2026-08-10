from __future__ import annotations

import pandas as pd

from src.screening.models import Signal
from src.screening.schema import (
    crossed_above,
    crossed_below,
    is_close_to,
    latest_number,
    normalize_indicator_frame,
    require_columns,
)


def detect_macro_cross(df: pd.DataFrame, gap_limit_pct: float = 1.5) -> tuple[Signal, ...]:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("SMA_50", "SMA_200"))
    sma50 = frame["SMA_50"]
    sma200 = frame["SMA_200"]
    golden = crossed_above(sma50, sma200)
    death = crossed_below(sma50, sma200)

    pair = frame[["SMA_50", "SMA_200"]].dropna()
    gap_pct = None
    converging = False
    if not pair.empty and pair.iloc[-1]["SMA_200"]:
        gaps = (
            (pair["SMA_200"] - pair["SMA_50"])
            / pair["SMA_200"].abs()
            * 100
        )
        gap_pct = float(gaps.iloc[-1])
        recent = gaps.tail(3)
        converging = bool(
            len(recent) >= 2
            and recent.iloc[-1] < recent.iloc[-2]
            and (len(recent) < 3 or recent.iloc[-2] <= recent.iloc[-3])
        )

    imminent = bool(
        gap_pct is not None
        and 0 < gap_pct <= gap_limit_pct
        and converging
    )
    values = {
        "sma_50": latest_number(frame, "SMA_50"),
        "sma_200": latest_number(frame, "SMA_200"),
        "gap_pct": round(gap_pct, 3) if gap_pct is not None else None,
    }
    return (
        Signal(
            "golden_cross",
            "Golden Cross",
            golden,
            "bullish",
            "SMA 50 crossed above SMA 200 on the latest bar.",
            values,
        ),
        Signal(
            "death_cross",
            "Death Cross",
            death,
            "bearish",
            "SMA 50 crossed below SMA 200 on the latest bar.",
            values,
        ),
        Signal(
            "imminent_golden_cross",
            "Imminent Golden Cross",
            imminent,
            "bullish",
            f"SMA 50 is below SMA 200 by at most {gap_limit_pct}% and the gap is converging.",
            values,
        ),
    )


def detect_silver_cross(df: pd.DataFrame) -> Signal:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("EMA_20", "EMA_50"))
    return Signal(
        "silver_cross",
        "Silver Cross",
        crossed_above(frame["EMA_20"], frame["EMA_50"]),
        "bullish",
        "EMA 20 crossed above EMA 50 on the latest bar.",
        {
            "ema_20": latest_number(frame, "EMA_20"),
            "ema_50": latest_number(frame, "EMA_50"),
        },
    )


def detect_strong_trend(df: pd.DataFrame, adx_threshold: float = 25) -> Signal:
    frame = normalize_indicator_frame(df)
    require_columns(
        frame,
        ("Close", "EMA_20", "EMA_50", "SMA_200", "ADX_14", "Plus_DI_14", "Minus_DI_14"),
    )
    values = {
        key: latest_number(frame, column)
        for key, column in {
            "price": "Close",
            "ema_20": "EMA_20",
            "ema_50": "EMA_50",
            "sma_200": "SMA_200",
            "adx": "ADX_14",
            "plus_di": "Plus_DI_14",
            "minus_di": "Minus_DI_14",
        }.items()
    }
    active = all(value is not None for value in values.values()) and bool(
        values["price"] > values["ema_20"] > values["ema_50"] > values["sma_200"]
        and values["adx"] > adx_threshold
        and values["plus_di"] > values["minus_di"]
    )
    return Signal(
        "strong_uptrend",
        "Strong Trend Confirmation",
        active,
        "bullish",
        "Price and moving averages are bullishly stacked with ADX confirmation and +DI leadership.",
        values,
    )


def detect_dynamic_support(
    df: pd.DataFrame,
    tolerance_pct: float = 1.5,
) -> tuple[Signal, ...]:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Close", "EMA_20", "EMA_50", "SMA_50", "SMA_200"))
    price = latest_number(frame, "Close")
    previous_price = float(frame["Close"].dropna().iloc[-2]) if frame["Close"].count() >= 2 else None
    ema20 = latest_number(frame, "EMA_20")
    ema50 = latest_number(frame, "EMA_50")
    sma50 = latest_number(frame, "SMA_50")
    sma200 = latest_number(frame, "SMA_200")
    uptrend = all(v is not None for v in (price, ema20, ema50, sma50, sma200)) and bool(
        price > sma200 and ema20 > ema50 and sma50 > sma200
    )
    pulling_back = previous_price is not None and price <= previous_price
    common = {
        "price": price,
        "previous_price": previous_price,
        "tolerance_pct": tolerance_pct,
    }
    return (
        Signal(
            "ema20_support_pullback",
            "EMA 20 Dynamic Support",
            bool(uptrend and pulling_back and is_close_to(price, ema20, tolerance_pct)),
            "bullish",
            "Price pulled back near EMA 20 while the broader trend remains bullish.",
            {**common, "support": ema20},
        ),
        Signal(
            "sma50_support_pullback",
            "SMA 50 Dynamic Support",
            bool(uptrend and pulling_back and is_close_to(price, sma50, tolerance_pct)),
            "bullish",
            "Price pulled back near SMA 50 while the broader trend remains bullish.",
            {**common, "support": sma50},
        ),
    )


def trend_signals(df: pd.DataFrame) -> tuple[Signal, ...]:
    return (
        *detect_macro_cross(df),
        detect_silver_cross(df),
        detect_strong_trend(df),
        *detect_dynamic_support(df),
    )

