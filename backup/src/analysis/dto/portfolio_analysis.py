from dataclasses import dataclass

from src.recommendation.dto.recommendation import Recommendation


@dataclass(slots=True)
class PortfolioAnalysis:

    stocks: list[Recommendation]

    portfolio_score: float

    health: str

    diversification: str

    concentration_risk: str

    summary: str