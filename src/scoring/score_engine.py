from src.analysis.stock_analyzer import StockAnalyzer

from src.scoring.dto.stock_score import StockScore
from src.scoring.rules.base_rule import ScoreRule

from src.scoring.rules.trend_rule import TrendRule
from src.scoring.rules.momentum_rule import MomentumRule
from src.scoring.rules.risk_rule import RiskRule
from src.scoring.rules.volatility_rule import VolatilityRule


class ScoreEngine:

    def __init__(
        self,
        rules: list[ScoreRule] | None = None,
    ):

        self.rules = rules or [
            TrendRule(),
            MomentumRule(),
            RiskRule(),
            VolatilityRule(),
        ]

    def score(
        self,
        analysis: StockAnalyzer,
    ) -> StockScore:

        total_score = 0
        max_score = 0
        results = []

        for rule in self.rules:

            result = rule.evaluate(analysis)

            results.append(result)

            total_score += result.points
            max_score += rule.MAX_SCORE

        return StockScore(
            score=total_score,
            max_score=max_score,
            results=results,
        )