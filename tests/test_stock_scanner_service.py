from __future__ import annotations

from dataclasses import dataclass
import unittest

from src.models.company import Company
from src.models.portfolio_holding import PortfolioHolding
from src.models.watchlist_item import WatchlistItem
from src.services.stock_scanner_service import StockScannerService


class CompanyRepositoryStub:
    def __init__(self):
        self.companies = {
            1: Company(id=1, symbol="ONE", company_name="One Ltd"),
            2: Company(id=2, symbol="TWO", company_name="Two Ltd"),
        }

    def get(self, company_id):
        return self.companies.get(company_id)


class PortfolioRepositoryStub:
    def get_all(self):
        return [PortfolioHolding(company_id=1, quantity=10, average_price=100)]


class WatchlistRepositoryStub:
    def list_all(self):
        return [
            WatchlistItem(1, "ONE", "One Ltd"),
            WatchlistItem(2, "TWO", "Two Ltd"),
        ]


@dataclass
class ScoreStub:
    score: int


@dataclass
class RiskStub:
    risk_reward_ratio: float


@dataclass
class ReportStub:
    score: ScoreStub
    risk: RiskStub


@dataclass
class ResultStub:
    symbol: str
    report: ReportStub


class IntelligenceServiceStub:
    def analyze(self, company_id, **kwargs):
        if company_id == 2:
            raise ValueError("insufficient history")
        return ResultStub("ONE", ReportStub(ScoreStub(70), RiskStub(3.0)))


class StockScannerServiceTests(unittest.TestCase):
    def test_deduplicates_sources_and_isolates_failures(self):
        service = StockScannerService(
            CompanyRepositoryStub(),
            PortfolioRepositoryStub(),
            WatchlistRepositoryStub(),
            IntelligenceServiceStub(),
        )
        result = service.scan(account_capital=100_000)
        self.assertEqual(len(result.stocks), 1)
        self.assertEqual(result.stocks[0].sources, ("Holding", "Watchlist"))
        self.assertEqual(result.failures[0].symbol, "TWO")

    def test_requires_at_least_one_universe(self):
        service = StockScannerService(
            CompanyRepositoryStub(),
            PortfolioRepositoryStub(),
            WatchlistRepositoryStub(),
            IntelligenceServiceStub(),
        )
        with self.assertRaisesRegex(ValueError, "at least one"):
            service.scan(
                account_capital=100_000,
                include_holdings=False,
                include_watchlist=False,
            )


if __name__ == "__main__":
    unittest.main()
