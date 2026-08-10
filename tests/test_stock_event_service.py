import unittest
from dataclasses import dataclass
from datetime import date

from src.models.stock_event import StockEvent
from src.services.stock_event_service import StockEventService


@dataclass
class Record:
    company_id: int


@dataclass
class Company:
    id: int
    symbol: str
    company_name: str


class CompanyRepository:
    def __init__(self):
        self.companies = {
            1: Company(1, "RELIANCE", "Reliance Industries"),
            2: Company(2, "INFY", "Infosys"),
        }

    def get(self, company_id):
        return self.companies.get(company_id)


class PortfolioRepository:
    def get_all(self):
        return [Record(1)]


class WatchlistRepository:
    def list_all(self):
        return [Record(1), Record(2)]


class Provider:
    def get_stock_events(self, symbol, start_date, end_date):
        if symbol == "INFY":
            raise RuntimeError("calendar unavailable")
        return [
            StockEvent(
                symbol=symbol,
                event_date=date(2026, 8, 20),
                event_type="Quarterly Results",
                title="Quarterly results expected",
                is_estimated=True,
            ),
            StockEvent(
                symbol=symbol,
                event_date=date(2025, 1, 1),
                event_type="Dividend",
                title="Dividend",
            ),
        ]


class StockEventServiceTests(unittest.TestCase):
    def setUp(self):
        self.service = StockEventService(
            company_repository=CompanyRepository(),
            portfolio_repository=PortfolioRepository(),
            watchlist_repository=WatchlistRepository(),
            provider=Provider(),
        )

    def test_deduplicates_universe_and_preserves_sources(self):
        result = self.service.list_events(
            upcoming_days=30,
            recent_days=30,
            as_of=date(2026, 8, 9),
        )

        self.assertEqual(len(result.events), 1)
        self.assertEqual(result.events[0].event.symbol, "RELIANCE")
        self.assertEqual(result.events[0].sources, ("Holding", "Watchlist"))

    def test_isolates_provider_failure(self):
        result = self.service.list_events(
            upcoming_days=30,
            recent_days=30,
            as_of=date(2026, 8, 9),
        )

        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.failures[0].symbol, "INFY")

    def test_requires_a_universe(self):
        with self.assertRaises(ValueError):
            self.service.list_events(
                include_holdings=False,
                include_watchlist=False,
            )


if __name__ == "__main__":
    unittest.main()

