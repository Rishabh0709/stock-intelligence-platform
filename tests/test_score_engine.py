import unittest

from src.scoring.dto.score_result import ScoreResult
from src.scoring.score_engine import ScoreEngine


class RuleStub:
    MAX_SCORE = 10

    def __init__(self, points):
        self.points = points

    def evaluate(self, analysis):
        return ScoreResult("stub", self.points, self.points > 0, "test evidence")


class ScoreEngineTests(unittest.TestCase):
    def test_aggregates_rules_and_normalizes_score(self):
        score = ScoreEngine([RuleStub(10), RuleStub(-5)]).score(object())
        self.assertEqual(score.score, 5)
        self.assertEqual(score.max_score, 20)
        self.assertEqual(score.normalized_score, 62.5)


if __name__ == "__main__":
    unittest.main()
