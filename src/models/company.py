from dataclasses import dataclass, field
from datetime import datetime
from src.utils.time import utc_now


@dataclass(slots=True)
class Company:
    """
    Represents a listed company in our platform.
    """
    
    symbol: str
    company_name: str
    id: int | None = None


    exchange: str = "NSE"

    isin: str | None = None

    sector: str | None = None

    industry: str | None = None

    country: str = "India"

    currency: str = "INR"

    website: str | None = None

    business_description: str | None = None

    created_at: datetime = field(default_factory=utc_now)