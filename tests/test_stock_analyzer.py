import unittest

from src.analysis.stock_analyzer import StockAnalyzer
from tests.fixtures import make_stock


class StockAnalyzerTests(unittest.TestCase):
    def test_exposes_canonical_analysis_components(self):
        analyzer = StockAnalyzer(make_stock())
        for name in ("trend", "momentum", "risk", "volatility", "returns", "drawdown"):
            self.assertIsNotNone(getattr(analyzer, name))


if __name__ == "__main__":
    unittest.main()
