from __future__ import annotations

import math

import pandas as pd

from src.screening.models import RiskMetrics
from src.screening.schema import latest_number, normalize_indicator_frame


def find_nearest_resistance(
    df: pd.DataFrame,
    *,
    lookback: int = 60,
    pivot_window: int = 3,
) -> float | None:
    """Find the nearest confirmed swing high above price.

    If no qualifying swing high exists, use the 52-week high (252 bars). A
    resistance at or below the current price is not a valid upside target.
    """
    if lookback < pivot_window * 2 + 1:
        raise ValueError("lookback is too short for the selected pivot_window")
    if pivot_window < 1:
        raise ValueError("pivot_window must be at least 1")
    frame = normalize_indicator_frame(df)
    current_price = latest_number(frame, "Close")
    if current_price is None:
        return None
    highs = frame["High"].dropna().tail(lookback)
    pivots: list[float] = []
    for offset in range(pivot_window, len(highs) - pivot_window):
        candidate = float(highs.iloc[offset])
        neighborhood = highs.iloc[
            offset - pivot_window: offset + pivot_window + 1
        ]
        surrounding = neighborhood.drop(neighborhood.index[pivot_window])
        if candidate > float(surrounding.max()) and candidate > current_price:
            pivots.append(candidate)
    if pivots:
        return round(min(pivots), 2)
    high_52w = frame["High"].dropna().tail(252)
    if high_52w.empty:
        return None
    fallback = float(high_52w.max())
    return round(fallback, 2) if fallback > current_price else None


def calculate_initial_stop(entry_price: float, atr: float, multiple: float = 2.0) -> float:
    _validate_positive("entry_price", entry_price)
    _validate_positive("atr", atr)
    _validate_positive("multiple", multiple)
    return round(max(0.0, entry_price - multiple * atr), 2)


def calculate_trailing_stop(highest_price: float, atr: float, multiple: float = 2.5) -> float:
    _validate_positive("highest_price", highest_price)
    _validate_positive("atr", atr)
    _validate_positive("multiple", multiple)
    return round(max(0.0, highest_price - multiple * atr), 2)


def calculate_position_size(
    account_capital: float,
    risk_percent: float,
    atr: float,
    stop_multiple: float = 2.0,
) -> int:
    _validate_positive("account_capital", account_capital)
    _validate_positive("risk_percent", risk_percent)
    _validate_positive("atr", atr)
    _validate_positive("stop_multiple", stop_multiple)
    if risk_percent > 100:
        raise ValueError("risk_percent cannot exceed 100")
    risk_amount = account_capital * risk_percent / 100
    return max(0, math.floor(risk_amount / (stop_multiple * atr)))


def calculate_risk_metrics(
    *,
    entry_price: float,
    atr: float,
    account_capital: float,
    risk_percent: float,
    resistance: float | None,
    highest_price_since_entry: float | None = None,
    minimum_rrr: float = 2.5,
) -> RiskMetrics:
    _validate_positive("minimum_rrr", minimum_rrr)
    initial_stop = calculate_initial_stop(entry_price, atr)
    highest = highest_price_since_entry or entry_price
    if highest < entry_price:
        raise ValueError("highest_price_since_entry cannot be below entry_price")
    trailing_stop = calculate_trailing_stop(highest, atr)
    risk_per_share = entry_price - initial_stop
    reward = None if resistance is None else max(0.0, resistance - entry_price)
    rrr = None if reward is None or risk_per_share <= 0 else reward / risk_per_share
    quantity = calculate_position_size(account_capital, risk_percent, atr)
    risk_amount = account_capital * risk_percent / 100
    eligible = bool(rrr is not None and rrr >= minimum_rrr and quantity > 0)
    return RiskMetrics(
        entry_price=round(entry_price, 2),
        atr=round(atr, 2),
        initial_stop=initial_stop,
        trailing_stop=trailing_stop,
        resistance=round(resistance, 2) if resistance is not None else None,
        reward_per_share=round(reward, 2) if reward is not None else None,
        risk_per_share=round(risk_per_share, 2),
        risk_reward_ratio=round(rrr, 2) if rrr is not None else None,
        account_risk_amount=round(risk_amount, 2),
        quantity=quantity,
        position_value=round(quantity * entry_price, 2),
        eligible=eligible,
    )


def _validate_positive(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite value greater than zero")
