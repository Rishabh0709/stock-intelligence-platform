import unittest
from types import SimpleNamespace

from src.models.company import Company
from src.models.portfolio_holding import PortfolioHolding
from src.portfolio.portfolio_analyzer import PortfolioAnalyzer
from tests.fixtures import make_prices


class PortfolioAnalyzerTests(unittest.TestCase):
    def test_calculates_position_and_portfolio_totals(self):
        holding = PortfolioHolding(company_id=1, quantity=2, average_price=90)
        analyzer = PortfolioAnalyzer(
            portfolio_repository=SimpleNamespace(get_all=lambda: [holding]),
            company_repository=SimpleNamespace(
                get=lambda _: Company(id=1, symbol="RELIANCE", company_name="Reliance Industries")
            ),
            price_repository=SimpleNamespace(list_by_company=lambda _: make_prices(3)),
            recommendation_engine=SimpleNamespace(recommend=lambda _: "Hold"),
            score_engine=SimpleNamespace(score=lambda _: "score"),
        )
        result = analyzer.analyze()
        self.assertEqual(result.total_investment, 180)
        self.assertEqual(result.current_value, 204)
        self.assertEqual(result.total_profit_loss, 24)
        self.assertEqual(result.positions[0].allocation_percent, 100)


if __name__ == "__main__":
    unittest.main()
