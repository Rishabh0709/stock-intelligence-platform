import unittest
from types import SimpleNamespace
from unittest.mock import patch

from src.recommendation.investment_report_builder import InvestmentReportBuilder
from tests.fixtures import make_stock


class InvestmentReportBuilderTests(unittest.TestCase):
    def test_combines_analysis_score_and_recommendation(self):
        fake_analysis = SimpleNamespace(
            trend=SimpleNamespace(analyze=lambda: "trend"),
            momentum=SimpleNamespace(analyze=lambda: "momentum"),
            risk=SimpleNamespace(analyze=lambda: "risk"),
            volatility=SimpleNamespace(analyze=lambda: "volatility"),
        )
        builder = InvestmentReportBuilder()
        builder.score_engine = SimpleNamespace(score=lambda _: "score")
        builder.recommendation_engine = SimpleNamespace(recommend=lambda _: "recommendation")
        with patch(
            "src.recommendation.investment_report_builder.StockAnalyzer",
            return_value=fake_analysis,
        ):
            report = builder.build(make_stock())
        self.assertEqual(report.recommendation, "recommendation")
        self.assertEqual(report.trend, "trend")
        self.assertEqual(report.risk, "risk")


if __name__ == "__main__":
    unittest.main()
