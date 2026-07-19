from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class Drawdown:
    """
    Represents drawdown for a single trading day.
    """

    date: date

    drawdown: float | None