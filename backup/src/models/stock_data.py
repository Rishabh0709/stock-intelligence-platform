from dataclasses import dataclass

from src.models.company import Company
from src.analytics.core.price_series import PriceSeries

@dataclass(slots=True)
class StockData:
    """
    Represents all historical data available for a stock.

    This is the primary domain object consumed by analytics
    and dashboard services.
    """

    company: Company
    price_series: PriceSeries