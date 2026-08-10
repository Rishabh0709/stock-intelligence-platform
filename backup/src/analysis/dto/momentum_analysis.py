from dataclasses import dataclass
from datetime import date
from src.common.enums.momentum import Momentum

@dataclass(slots=True)
class MomentumAnalysis:
    """
    Result of momentum analysis.
    """

    date: date

    momentum: Momentum

    rsi: float | None

    macd: float | None

    signal: float | None

    histogram: float | None

    bullish_macd: bool

    bearish_macd: bool

    overbought: bool

    oversold: bool