from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class MACD:
    """
    Represents MACD values for a single trading day.
    """

    date: date

    macd: float | None

    signal: float | None

    histogram: float | None