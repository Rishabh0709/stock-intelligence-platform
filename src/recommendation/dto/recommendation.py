from dataclasses import dataclass

from src.scoring.dto.stock_score import StockScore


@dataclass(slots=True)
class Recommendation:
    """
    Final recommendation for a stock.
    """

    rating: str

    confidence: str

    summary: str

    strengths: list[str]

    weaknesses: list[str]

    score: StockScore