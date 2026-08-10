import unittest

from src.analysis.trend_analyzer import TrendAnalyzer
from src.common.enums.trend import Trend, TrendStrength
from tests.fixtures import make_stock


class TrendAnalyzerTests(unittest.TestCase):
    def setUp(self):
        self.analyzer = TrendAnalyzer(make_stock())

    def test_bullish_ordering(self):
        self.assertEqual(self.analyzer._classify_trend(120, 115, 110, 100), Trend.BULLISH)

    def test_missing_average_is_neutral(self):
        self.assertEqual(self.analyzer._classify_trend(120, None, 110, 100), Trend.NEUTRAL)

    def test_strength_threshold(self):
        self.assertEqual(self.analyzer._classify_strength(30), TrendStrength.STRONG)


if __name__ == "__main__":
    unittest.main()
