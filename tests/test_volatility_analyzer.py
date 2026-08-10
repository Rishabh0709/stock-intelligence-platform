import unittest

from src.analysis.volatility_analyzer import VolatilityAnalyzer
from tests.fixtures import make_stock


class VolatilityAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = VolatilityAnalyzer(make_stock())

    def test_classification_thresholds(self):
        self.assertEqual(self.analyzer._classify(None), "Unknown")
        self.assertEqual(self.analyzer._classify(0.25), "Moderate")
        self.assertEqual(self.analyzer._classify(0.45), "Very High")


if __name__ == "__main__":
    unittest.main()
