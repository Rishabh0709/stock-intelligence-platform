from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.recommendation.dto.recommendation import Recommendation
from src.scoring.dto.stock_score import StockScore

if TYPE_CHECKING:
    from src.analysis.stock_analyzer import StockAnalyzer


@dataclass(slots=True)
class PortfolioPosition:

    symbol: str

    quantity: float

    average_price: float

    current_price: float

    invested_value: float

    current_value: float

    profit_loss: float

    profit_loss_percent: float
    
    recommendation: Recommendation
    
    score: StockScore

    analysis: "StockAnalyzer"

    allocation_percent: float = 0.0

    @property
    def rating(self):
        return self.recommendation.rating

    @property
    def confidence(self):
        return self.recommendation.confidence
