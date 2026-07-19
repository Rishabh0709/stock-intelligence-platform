from dataclasses import dataclass
from datetime import date
from src.common.enums.trend import Trend, TrendStrength

@dataclass(slots=True)
class TrendAnalysis:
    """
    Result of technical trend analysis.
    """

    date: date

    trend: Trend

    strength: TrendStrength

    price: float | None

    sma20: float | None

    sma50: float | None

    sma200: float | None

    ema20: float | None

    adx: float | None

    price_above_sma20: bool

    price_above_sma50: bool

    sma20_above_sma50: bool

    sma50_above_sma200: bool