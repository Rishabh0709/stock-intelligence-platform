import unittest

from src.recommendation.recommendation_engine import RecommendationEngine
from src.scoring.dto.score_result import ScoreResult
from src.scoring.dto.stock_score import StockScore


class RecommendationEngineTests(unittest.TestCase):
    def test_builds_rating_and_explanations(self):
        score = StockScore(
            score=10,
            max_score=10,
            results=[ScoreResult("trend", 10, True, "trend is constructive")],
        )
        recommendation = RecommendationEngine().recommend(score)
        self.assertEqual(recommendation.rating, "Strong Buy")
        self.assertIn("trend is constructive", recommendation.strengths)
        self.assertIn("Strong Buy", recommendation.summary)


if __name__ == "__main__":
    unittest.main()
