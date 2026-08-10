import unittest

from src.analysis.risk_analyzer import RiskAnalyzer
from tests.fixtures import make_stock


class RiskAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = RiskAnalyzer(make_stock())

    def test_unknown_when_required_data_is_missing(self):
        self.assertEqual(self.analyzer._risk_level(None, -0.20), "Unknown")

    def test_high_risk_combination(self):
        self.assertEqual(self.analyzer._risk_level(0.45, -0.55), "High")

    def test_drawdown_classification(self):
        self.assertEqual(self.analyzer._drawdown_level(-0.36), "Severe")


if __name__ == "__main__":
    unittest.main()
