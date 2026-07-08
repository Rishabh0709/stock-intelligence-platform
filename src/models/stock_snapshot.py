from dataclasses import dataclass
from typing import Optional


@dataclass
class StockSnapshot:
    # Company
    symbol: str
    company_name: str
    exchange: str

    sector: Optional[str]
    industry: Optional[str]

    website: Optional[str]
    business_summary: Optional[str]

    country: Optional[str]
    currency: Optional[str]

    # Market Data
    current_price: Optional[float]
    previous_close: Optional[float]

    open_price: Optional[float]
    day_high: Optional[float]
    day_low: Optional[float]

    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]

    volume: Optional[int]
    average_volume: Optional[int]

    market_cap: Optional[int]
    enterprise_value: Optional[int]

    shares_outstanding: Optional[int]

    # Valuation

    trailing_pe: Optional[float]
    forward_pe: Optional[float]

    price_to_book: Optional[float]

    peg_ratio: Optional[float]

    # Profitability

    roe: Optional[float]

    roa: Optional[float]

    gross_margin: Optional[float]

    operating_margin: Optional[float]

    profit_margin: Optional[float]

    # Growth

    revenue_growth: Optional[float]

    earnings_growth: Optional[float]

    # Dividend

    dividend_rate: Optional[float]

    dividend_yield: Optional[float]

    payout_ratio: Optional[float]

    ex_dividend_date: Optional[str]