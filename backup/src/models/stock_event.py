from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class StockEvent:
    """Normalized market event returned by a data provider."""

    symbol: str
    event_date: date
    event_type: str
    title: str
    details: str | None = None
    amount: float | None = None
    ratio: float | None = None
    is_estimated: bool = False
    source: str = "Yahoo Finance"

