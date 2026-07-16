from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class ATR:
    """
    Represents Average True Range values for a single trading day.
    """

    date: date

    true_range: float | None

    atr: float | None