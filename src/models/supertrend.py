from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class SuperTrend:
    """
    Represents SuperTrend values for a single trading day.
    """

    date: date

    upper_band: float | None

    lower_band: float | None

    supertrend: float | None

    direction: str | None