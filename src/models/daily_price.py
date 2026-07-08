from dataclasses import dataclass
from datetime import date


@dataclass
class DailyPrice:

    company_id: int

    price_date: date

    open: float

    high: float

    low: float

    close: float

    adjusted_close: float

    volume: int

    dividend: float = 0.0

    stock_split: float = 0.0