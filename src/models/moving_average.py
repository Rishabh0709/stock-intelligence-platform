from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class MovingAverage:
    """
    Represents moving average values for a single trading day.
    """

    date: date

    sma: float | None

    ema: float | None