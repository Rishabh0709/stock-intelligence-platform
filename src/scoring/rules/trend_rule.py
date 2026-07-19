from src.analysis.stock_analyzer import StockAnalyzer

from src.scoring.dto.score_result import ScoreResult
from src.scoring.rules.base_rule import ScoreRule

from src.scoring.score_weights import (
    STRONG_BULLISH_TREND,
    WEAK_BULLISH_TREND,
    STRONG_BEARISH_TREND,
    WEAK_BEARISH_TREND,
    SIDEWAYS_TREND,
)

from src.common.enums.trend import (
    Trend,
    TrendStrength,
)


class TrendRule(ScoreRule):
    
    MAX_SCORE = 25
    
    def evaluate(
        self,
        analysis: StockAnalyzer,
    ) -> ScoreResult:

        trend = analysis.trend.analyze()

        if trend.trend == Trend.BULLISH:

            if trend.strength == TrendStrength.STRONG:

                return ScoreResult(
                    rule="Trend",
                    points=STRONG_BULLISH_TREND,
                    passed=True,
                    reason="Strong bullish trend",
                )

            return ScoreResult(
                rule="Trend",
                points=WEAK_BULLISH_TREND,
                passed=True,
                reason="Weak bullish trend",
            )

        if trend.trend == Trend.BEARISH:

            if trend.strength == TrendStrength.STRONG:

                return ScoreResult(
                    rule="Trend",
                    points=STRONG_BEARISH_TREND,
                    passed=False,
                    reason="Strong bearish trend",
                )

            return ScoreResult(
                rule="Trend",
                points=WEAK_BEARISH_TREND,
                passed=False,
                reason="Weak bearish trend",
            )

        return ScoreResult(
            rule="Trend",
            points=SIDEWAYS_TREND,
            passed=False,
            reason="Sideways trend",
        )