from dataclasses import dataclass

from src.models.company import Company
from src.recommendation.dto.recommendation import Recommendation
from src.scoring.dto.stock_score import StockScore


@dataclass(slots=True)
class ScreenerResult:
    """
    Represents one stock returned by the stock screener.
    """

    company: Company

    latest_price: float

    score: StockScore

    recommendation: Recommendation