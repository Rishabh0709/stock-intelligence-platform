from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class DailyPriceDTO:
    """
    Represents one day's market data received from an external provider.
    """

    price_date: date

    open_price: float

    high_price: float

    low_price: float

    close_price: float

    adjusted_close: float | None

    volume: int