import unittest
from types import SimpleNamespace

from src.analysis.momentum_analyzer import MomentumAnalyzer
from src.common.enums.momentum import Momentum
from tests.fixtures import make_stock


class MomentumAnalyzerTests(unittest.TestCase):
    def test_classifies_bullish_evidence(self):
        analyzer = MomentumAnalyzer(make_stock())
        analyzer.rsi.latest = lambda: 60.0
        analyzer.macd.latest = lambda: SimpleNamespace(macd=2.0, signal=1.0, histogram=1.0)
        result = analyzer.analyze()
        self.assertEqual(result.momentum, Momentum.BULLISH)
        self.assertTrue(result.bullish_macd)

    def test_missing_evidence_is_neutral(self):
        analyzer = MomentumAnalyzer(make_stock())
        analyzer.rsi.latest = lambda: None
        analyzer.macd.latest = lambda: None
        self.assertEqual(analyzer.analyze().momentum, Momentum.NEUTRAL)


if __name__ == "__main__":
    unittest.main()
