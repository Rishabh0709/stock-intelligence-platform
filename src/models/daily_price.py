from dataclasses import dataclass
from datetime import date
import math
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

    @property
    def market_price(self) -> float:
        """Unadjusted closing price used for holdings, alerts and orders."""
        return self.close_price

    @property
    def analysis_price(self) -> float:
        """Corporate-action-adjusted close used for returns and indicators."""
        if self.adjusted_close is None:
            return self.close_price
        try:
            value = float(self.adjusted_close)
        except (TypeError, ValueError):
            return self.close_price
        return value if math.isfinite(value) and value > 0 else self.close_price

    @property
    def adjustment_factor(self) -> float:
        """Factor that converts raw historical OHLC into analysis OHLC."""
        try:
            raw_close = float(self.close_price)
        except (TypeError, ValueError):
            return 1.0
        if not math.isfinite(raw_close) or raw_close <= 0:
            return 1.0
        return self.analysis_price / raw_close

    @property
    def analysis_open(self) -> float:
        return self.open_price * self.adjustment_factor

    @property
    def analysis_high(self) -> float:
        return self.high_price * self.adjustment_factor

    @property
    def analysis_low(self) -> float:
        return self.low_price * self.adjustment_factor
    
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
