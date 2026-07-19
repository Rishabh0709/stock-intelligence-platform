from dataclasses import dataclass

from src.portfolio.dto.portfolio_position import PortfolioPosition


@dataclass(slots=True)
class PortfolioAnalysis:

    positions: list[PortfolioPosition]

    total_investment: float

    current_value: float

    total_profit_loss: float

    total_profit_loss_percent: float

    winners: int

    losers: int