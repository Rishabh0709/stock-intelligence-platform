from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class SnapshotDTO:
    """
    Live market snapshot from an external provider.
    """

    symbol: str

    current_price: Optional[float] = None

    previous_close: Optional[float] = None

    open_price: Optional[float] = None

    day_high: Optional[float] = None

    day_low: Optional[float] = None

    fifty_two_week_high: Optional[float] = None

    fifty_two_week_low: Optional[float] = None

    volume: Optional[int] = None

    average_volume: Optional[int] = None

    market_cap: Optional[int] = None

    enterprise_value: Optional[int] = None

    shares_outstanding: Optional[int] = None

    trailing_pe: Optional[float] = None

    forward_pe: Optional[float] = None

    price_to_book: Optional[float] = None

    peg_ratio: Optional[float] = None

    dividend_yield: Optional[float] = None