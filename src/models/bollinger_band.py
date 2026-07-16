from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class BollingerBand:
    """
    Represents Bollinger Bands for a single trading day.
    """

    date: date

    upper: float | None

    middle: float | None

    lower: float | None