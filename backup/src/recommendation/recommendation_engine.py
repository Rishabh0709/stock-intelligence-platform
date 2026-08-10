from src.recommendation.dto.recommendation import Recommendation
from src.scoring.dto.stock_score import StockScore


class RecommendationEngine:
    """
    Converts a StockScore into an investment recommendation.
    """

    def recommend(
        self,
        score: StockScore,
    ) -> Recommendation:

        normalized = score.normalized_score

        if normalized >= 90:
            rating = "Strong Buy"
            confidence = "Very High"

        elif normalized >= 75:
            rating = "Buy"
            confidence = "High"

        elif normalized >= 60:
            rating = "Accumulate"
            confidence = "Moderate"

        elif normalized >= 40:
            rating = "Hold"
            confidence = "Moderate"

        elif normalized >= 25:
            rating = "Reduce"
            confidence = "High"

        else:
            rating = "Sell"
            confidence = "Very High"

        strengths = []
        weaknesses = []

        for result in score.results:

            if result.passed:
                strengths.append(result.reason)
            else:
                weaknesses.append(result.reason)

        summary = self._build_summary(
            rating=rating,
            strengths=strengths,
            weaknesses=weaknesses,
        )

        return Recommendation(
            rating=rating,
            confidence=confidence,
            summary=summary,
            strengths=strengths,
            weaknesses=weaknesses,
            score=score,
        )

    def _build_summary(
        self,
        rating: str,
        strengths: list[str],
        weaknesses: list[str],
    ) -> str:

        summary = f"Overall recommendation: {rating}."

        if strengths:
            summary += f" Strengths include {', '.join(strengths)}."

        if weaknesses:
            summary += f" Weaknesses include {', '.join(weaknesses)}."

        return summary