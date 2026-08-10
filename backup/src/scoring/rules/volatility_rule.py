from src.analysis.stock_analyzer import StockAnalyzer

from src.scoring.dto.score_result import ScoreResult
from src.scoring.rules.base_rule import ScoreRule

from src.scoring.score_weights import (
    LOW_VOLATILITY,
    MEDIUM_VOLATILITY,
    HIGH_VOLATILITY,
    NEAR_LOWER_BAND,
    NEAR_UPPER_BAND,
)


class VolatilityRule(ScoreRule):

    MAX_SCORE = LOW_VOLATILITY + NEAR_LOWER_BAND

    def evaluate(
        self,
        analysis: StockAnalyzer,
    ) -> ScoreResult:

        volatility = analysis.volatility.analyze()

        score = 0

        reasons = []

        # Volatility Level
        if volatility.volatility_level == "Low":

            score += LOW_VOLATILITY
            reasons.append("Low Volatility")

        elif volatility.volatility_level == "Moderate":

            score += MEDIUM_VOLATILITY
            reasons.append("Moderate Volatility")

        elif volatility.volatility_level in {"High", "Very High"}:

            score += HIGH_VOLATILITY
            reasons.append(
                f"{volatility.volatility_level} Volatility"
            )

        else:
            reasons.append("Volatility unavailable")

        # Bollinger Position
        if volatility.near_lower_band:

            score += NEAR_LOWER_BAND
            reasons.append("Near Lower Band")

        elif volatility.near_upper_band:

            score += NEAR_UPPER_BAND
            reasons.append("Near Upper Band")

        return ScoreResult(
            rule="Volatility",
            points=score,
            passed=score > 0,
            reason=", ".join(reasons) if reasons else "Neutral Volatility",
        )
