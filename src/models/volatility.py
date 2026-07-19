from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class Volatility:
    """
    Represents historical volatility for a single trading day.
    """

    date: date

    volatility: float | None