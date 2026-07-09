from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CompanyDTO:
    """
    Company information received from an external provider.
    """

    symbol: str
    company_name: str
    exchange: str

    isin: Optional[str] = None

    sector: Optional[str] = None

    industry: Optional[str] = None

    country: Optional[str] = None

    currency: Optional[str] = None

    website: Optional[str] = None

    business_description: Optional[str] = None