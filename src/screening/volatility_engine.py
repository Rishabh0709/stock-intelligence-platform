from __future__ import annotations

import pandas as pd

from src.screening.models import Signal
from src.screening.schema import latest_number, normalize_indicator_frame, require_columns


def _volume_average_before_latest(frame: pd.DataFrame, period: int = 20) -> float | None:
    values = frame["Volume"].dropna()
    if len(values) < period + 1:
        return None
    reference = values.iloc[-(period + 1):-1]
    return float(reference.mean())


def detect_bollinger_squeeze(df: pd.DataFrame) -> tuple[Signal, ...]:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("BB_Upper", "BB_Lower", "EMA_20", "ATR_14", "Volume"))
    usable = frame[["BB_Upper", "BB_Lower", "EMA_20", "ATR_14", "Volume"]].dropna().copy()
    if usable.empty:
        current_squeeze = breakout = False
        kc_upper = kc_lower = volume_ratio = None
    else:
        usable["KC_Upper"] = usable["EMA_20"] + 2 * usable["ATR_14"]
        usable["KC_Lower"] = usable["EMA_20"] - 2 * usable["ATR_14"]
        squeeze_state = (
            (usable["BB_Upper"] < usable["KC_Upper"])
            & (usable["BB_Lower"] > usable["KC_Lower"])
        )
        current_squeeze = bool(squeeze_state.iloc[-1])
        recently_squeezed = bool(squeeze_state.iloc[-4:-1].any()) if len(usable) >= 2 else False
        expanded = bool(
            usable.iloc[-1]["BB_Upper"] > usable.iloc[-1]["KC_Upper"]
            and usable.iloc[-1]["BB_Lower"] < usable.iloc[-1]["KC_Lower"]
        )
        volume_sma = _volume_average_before_latest(frame)
        current_volume = float(usable.iloc[-1]["Volume"])
        volume_ratio = current_volume / volume_sma if volume_sma and volume_sma > 0 else None
        breakout = bool(recently_squeezed and expanded and volume_ratio is not None and volume_ratio > 1.5)
        kc_upper = float(usable.iloc[-1]["KC_Upper"])
        kc_lower = float(usable.iloc[-1]["KC_Lower"])
    values = {
        "bb_upper": latest_number(frame, "BB_Upper"),
        "bb_lower": latest_number(frame, "BB_Lower"),
        "keltner_upper": kc_upper,
        "keltner_lower": kc_lower,
        "volume_ratio": round(volume_ratio, 3) if volume_ratio is not None else None,
    }
    return (
        Signal(
            "bollinger_keltner_squeeze",
            "Bollinger/Keltner Squeeze",
            current_squeeze,
            "neutral",
            "Bollinger Bands are inside Keltner Channels, indicating volatility compression.",
            values,
        ),
        Signal(
            "squeeze_breakout",
            "Squeeze Breakout",
            breakout,
            "bullish",
            "A recent squeeze released with band expansion and volume above 1.5x its 20-bar average.",
            values,
        ),
    )


def detect_vcp(df: pd.DataFrame) -> tuple[Signal, ...]:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Close", "ATR_14", "Volume"))
    usable = frame[["Close", "ATR_14", "Volume"]].dropna()
    setup = breakout = False
    atr_means: list[float] = []
    volume_means: list[float] = []
    if len(usable) >= 36:
        # Measure three completed contraction cycles before the signal bar.
        old = usable.iloc[-36:-16]
        middle = usable.iloc[-16:-6]
        recent = usable.iloc[-6:-1]
        cycles = (old, middle, recent)
        atr_means = [float((cycle["ATR_14"] / cycle["Close"]).mean()) for cycle in cycles]
        volume_means = [float(cycle["Volume"].mean()) for cycle in cycles]
        setup = bool(
            atr_means[0] > atr_means[1] > atr_means[2]
            and volume_means[0] > volume_means[1] > volume_means[2]
        )
        prior_high = float(usable["Close"].iloc[-21:-1].max())
        prior_volume = float(usable["Volume"].iloc[-21:-1].mean())
        breakout = bool(
            setup
            and usable.iloc[-1]["Close"] > prior_high
            and usable.iloc[-1]["Volume"] > 1.5 * prior_volume
        )
    values = {
        "atr_pct_cycles": ",".join(f"{value:.4f}" for value in atr_means) or None,
        "volume_cycles": ",".join(f"{value:.0f}" for value in volume_means) or None,
    }
    return (
        Signal(
            "vcp_setup",
            "Volatility Contraction Pattern",
            setup,
            "bullish",
            "ATR as a percentage of price and average volume contracted across 20/10/5-bar cycles.",
            values,
        ),
        Signal(
            "vcp_breakout",
            "VCP Price Expansion",
            breakout,
            "bullish",
            "A VCP setup broke its prior 20-bar closing high with at least 1.5x volume.",
            values,
        ),
    )


def detect_band_touch_reversal(df: pd.DataFrame) -> Signal:
    frame = normalize_indicator_frame(df)
    require_columns(frame, ("Close", "BB_Lower"))
    recent = frame[["Close", "BB_Lower"]].dropna()
    active = bool(
        len(recent) >= 2
        and recent.iloc[-2]["Close"] < recent.iloc[-2]["BB_Lower"]
        and recent.iloc[-1]["Close"] >= recent.iloc[-1]["BB_Lower"]
    )
    return Signal(
        "lower_band_reversal",
        "Lower Bollinger Band Reversal",
        active,
        "bullish",
        "Price closed below the lower band and returned inside it on the next bar.",
        {
            "price": latest_number(frame, "Close"),
            "lower_band": latest_number(frame, "BB_Lower"),
        },
    )


def volatility_signals(df: pd.DataFrame) -> tuple[Signal, ...]:
    return (
        *detect_bollinger_squeeze(df),
        *detect_vcp(df),
        detect_band_touch_reversal(df),
    )
