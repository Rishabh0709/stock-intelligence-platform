from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class RSI:
    date: date
    rsi: float | None