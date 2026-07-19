from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class VolatilityAnalysis:
    """
    Volatility analysis of a stock.
    """

    date: date

    volatility: float | None

    atr: float | None

    upper_band: float | None

    middle_band: float | None

    lower_band: float | None

    volatility_level: str

    near_upper_band: bool

    near_lower_band: bool