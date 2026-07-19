from dataclasses import dataclass

from src.recommendation.dto.recommendation import Recommendation


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

    @property
    def rating(self):
        return self.recommendation.rating

    @property
    def confidence(self):
        return self.recommendation.confidence