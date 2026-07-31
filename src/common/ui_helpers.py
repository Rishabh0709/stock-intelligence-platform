from src.common.enums.recommendation import Recommendation


def recommendation_badge(recommendation: Recommendation) -> str:
    if recommendation == Recommendation.BUY:
        return "🟢 BUY"

    if recommendation == Recommendation.HOLD:
        return "🟡 HOLD"

    if recommendation == Recommendation.SELL:
        return "🔴 SELL"

    return "⚪ UNKNOWN"