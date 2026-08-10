from __future__ import annotations

import pandas as pd

from src.screening.models import IntelligenceScore, ScoreComponent
from src.screening.schema import latest_number, normalize_indicator_frame, require_columns
from src.screening.trend_engine import detect_dynamic_support
from src.screening.volatility_engine import detect_bollinger_squeeze, detect_vcp


def _category(score: int) -> str:
    if score >= 80:
        return "High Conviction Buy / Breakout Candidate"
    if score >= 60:
        return "Watchlist / Pullback Buy Candidate"
    if score >= 40:
        return "Neutral / Sideways Range"
    return "Bearish / Avoid"


def _linear_slope(values: pd.Series) -> float | None:
    clean = values.dropna().astype(float)
    if len(clean) < 2:
        return None
    x_mean = (len(clean) - 1) / 2
    y_mean = float(clean.mean())
    numerator = sum(
        (index - x_mean) * (value - y_mean)
        for index, value in enumerate(clean)
    )
    denominator = sum((index - x_mean) ** 2 for index in range(len(clean)))
    return numerator / denominator if denominator else None


def calculate_stock_score(df: pd.DataFrame) -> IntelligenceScore:
    """Calculate the explicit, explainable 0-100 intelligence score."""
    frame = normalize_indicator_frame(df)
    require_columns(
        frame,
        (
            "Close", "SMA_50", "SMA_200", "EMA_20", "EMA_50", "ADX_14",
            "MACD", "MACD_Signal", "RSI_14", "OBV", "Volume", "ATR_14",
            "BB_Upper", "BB_Lower",
        ),
    )
    price = latest_number(frame, "Close")
    sma50 = latest_number(frame, "SMA_50")
    sma200 = latest_number(frame, "SMA_200")
    adx = latest_number(frame, "ADX_14")
    macd = latest_number(frame, "MACD")
    macd_signal = latest_number(frame, "MACD_Signal")
    rsi = latest_number(frame, "RSI_14")
    volume = latest_number(frame, "Volume")
    volumes = frame["Volume"].dropna()
    volume_reference = volumes.iloc[-21:-1] if len(volumes) >= 21 else pd.Series(dtype=float)
    volume_sma20 = float(volume_reference.mean()) if len(volume_reference) == 20 else None
    obv_slope = _linear_slope(frame["OBV"].tail(20))
    obv_slope_positive = bool(obv_slope is not None and obv_slope > 0)
    squeeze = detect_bollinger_squeeze(frame)[0].active
    vcp = detect_vcp(frame)[0].active
    pullback = any(signal.active for signal in detect_dynamic_support(frame))

    definitions = (
        ("price_above_sma200", "Price > SMA 200", 10, price is not None and sma200 is not None and price > sma200),
        ("sma50_above_sma200", "SMA 50 > SMA 200", 10, sma50 is not None and sma200 is not None and sma50 > sma200),
        ("adx_trend", "ADX > 25", 10, adx is not None and adx > 25),
        ("macd_bullish", "MACD > Signal", 15, macd is not None and macd_signal is not None and macd > macd_signal),
        ("healthy_rsi", "RSI in 50-65", 10, rsi is not None and 50 <= rsi <= 65),
        ("obv_rising", "OBV slope > 0", 15, obv_slope_positive),
        ("volume_above_average", "Volume > SMA 20 Volume", 10, volume is not None and volume_sma20 is not None and volume > volume_sma20),
        ("volatility_contraction", "ATR contraction / squeeze", 10, squeeze or vcp),
        ("ema20_support", "Pullback to dynamic support", 10, pullback),
    )
    components = tuple(
        ScoreComponent(
            key=key,
            label=label,
            points=max_points if passed else 0,
            max_points=max_points,
            passed=bool(passed),
            explanation=f"{label}: {'passed' if passed else 'not met'}.",
        )
        for key, label, max_points, passed in definitions
    )
    score = sum(component.points for component in components)
    return IntelligenceScore(score=score, category=_category(score), components=components)
