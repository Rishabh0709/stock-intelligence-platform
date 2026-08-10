from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class PortfolioHolding:
    """
    Represents a stock currently held in the user's portfolio.
    """

    id: int | None = None

    company_id: int | None = None

    quantity: float = 0.0

    average_price: float = 0.0

    created_at: datetime | None = None

    updated_at: datetime | None = None