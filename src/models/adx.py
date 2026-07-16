from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class ADX:
    """
    Represents Average Directional Index (ADX)
    values for a single trading day.
    """

    date: date

    plus_di: float | None

    minus_di: float | None

    adx: float | None