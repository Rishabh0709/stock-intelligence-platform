from src.analysis.stock_analyzer import StockAnalyzer

from src.scoring.dto.score_result import ScoreResult
from src.scoring.rules.base_rule import ScoreRule

from src.scoring.score_weights import (
    LOW_RISK,
    MEDIUM_RISK,
    HIGH_RISK,
    HEALTHY_DRAWDOWN,
    NORMAL_DRAWDOWN,
    DEEP_DRAWDOWN,
    SEVERE_DRAWDOWN,
)


class RiskRule(ScoreRule):

    MAX_SCORE = LOW_RISK + HEALTHY_DRAWDOWN

    def evaluate(
        self,
        analysis: StockAnalyzer,
    ) -> ScoreResult:

        risk = analysis.risk.analyze()

        score = 0

        reasons = []

        # Risk Level
        if risk.risk_level == "Low":
            score += LOW_RISK
            reasons.append("Low Risk")

        elif risk.risk_level == "Medium":
            score += MEDIUM_RISK
            reasons.append("Medium Risk")

        elif risk.risk_level == "High":
            score += HIGH_RISK
            reasons.append("High Risk")

        else:
            reasons.append("Risk unavailable")

        # Drawdown
        if risk.drawdown_level == "Healthy":
            score += HEALTHY_DRAWDOWN
            reasons.append("Healthy Drawdown")

        elif risk.drawdown_level == "Normal":
            score += NORMAL_DRAWDOWN
            reasons.append("Normal Drawdown")

        elif risk.drawdown_level == "Deep":
            score += DEEP_DRAWDOWN
            reasons.append("Deep Drawdown")

        elif risk.drawdown_level == "Severe":
            score += SEVERE_DRAWDOWN
            reasons.append("Severe Drawdown")

        else:
            reasons.append("Drawdown unavailable")

        return ScoreResult(
            rule="Risk",
            points=score,
            passed=score > 0,
            reason=", ".join(reasons),
        )
