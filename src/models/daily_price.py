from dataclasses import dataclass, asdict
from datetime import date
from typing import Optional


@dataclass(slots=True)
class DailyPrice:
    """
    Represents one day's trading data for a company.
    """

    company_id: int

    price_date: date

    open_price: float

    high_price: float

    low_price: float

    close_price: float

    adjusted_close: Optional[float]

    volume: int
    
    def to_dict(self) -> dict:
        return {
        "company_id": self.company_id,
        "price_date": self.price_date,
        "open": self.open_price,
        "high": self.high_price,
        "low": self.low_price,
        "close": self.close_price,
        "adjusted_close": self.adjusted_close,
        "volume": self.volume,
        }