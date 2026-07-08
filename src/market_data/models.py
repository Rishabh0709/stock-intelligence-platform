from dataclasses import dataclass
from datetime import date


@dataclass
class DailyPrice:

    company_id: int

    date: date

    open: float

    high: float

    low: float

    close: float

    adjusted_close: float

    volume: int

    dividends: float | None = None

    stock_split: float | None = None