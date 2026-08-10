from dataclasses import dataclass

from src.analysis.dto.trend_analysis import TrendAnalysis
from src.analysis.dto.momentum_analysis import MomentumAnalysis
from src.analysis.dto.risk_analysis import RiskAnalysis
from src.analysis.dto.volatility_analysis import VolatilityAnalysis

from src.recommendation.dto.recommendation import Recommendation


@dataclass(slots=True)
class InvestmentReport:
    """
    Complete investment report for a stock.
    """

    recommendation: Recommendation

    trend: TrendAnalysis

    momentum: MomentumAnalysis

    risk: RiskAnalysis

    volatility: VolatilityAnalysis