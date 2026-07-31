from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class WatchlistItem:
    company_id: int
    symbol: str
    company_name: str
    id: int | None = None
    entry_price: float | None = None
    target_price: float | None = None
    alert_price: float | None = None
    priority: str = "Medium"
    status: str = "Watching"
    thesis: str | None = None
    notes: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
