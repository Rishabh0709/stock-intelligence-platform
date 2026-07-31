import unittest
from datetime import date

from sqlalchemy import create_engine

from src.database.tables import metadata
from src.models.company import Company
from src.models.daily_price import DailyPrice
from src.repositories.company_repository import SQLiteCompanyRepository
from src.repositories.price_repository import SQLitePriceRepository
from src.repositories.watchlist_repository import SQLiteWatchlistRepository
from src.services.watchlist_service import WatchlistService


class MemoryDatabase:
    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:")
        metadata.create_all(self.engine)


class FakeCompanyService:
    def __init__(self, repository):
        self.repository = repository

    def ensure_company(self, symbol):
        company = self.repository.get_by_symbol(symbol)
        if company is None:
            company = self.repository.save(
                Company(
                    symbol=symbol,
                    company_name=f"{symbol} Limited",
                )
            )
        return company


class WatchlistServiceTest(unittest.TestCase):
    def setUp(self):
        database = MemoryDatabase()
        self.company_repository = SQLiteCompanyRepository(database)
        self.price_repository = SQLitePriceRepository(database)
        self.repository = SQLiteWatchlistRepository(database)
        self.service = WatchlistService(
            repository=self.repository,
            company_service=FakeCompanyService(self.company_repository),
            price_repository=self.price_repository,
        )

    def test_save_update_overview_and_remove(self):
        saved = self.service.save(
            symbol="RELIANCE",
            entry_price=1400,
            target_price=1650,
            priority="High",
            thesis="Earnings growth",
        )
        self.assertEqual(saved.symbol, "RELIANCE")
        self.assertEqual(len(self.service.list_all()), 1)

        self.price_repository.save(
            DailyPrice(
                company_id=saved.company_id,
                price_date=date(2026, 7, 28),
                open_price=1490,
                high_price=1510,
                low_price=1480,
                close_price=1500,
                adjusted_close=1500,
                volume=100,
            )
        )

        overview = self.service.get_overview()[0]
        self.assertEqual(overview.current_price, 1500)
        self.assertEqual(overview.upside_to_target_percent, 10.0)
        self.assertFalse(overview.alert_triggered)

        updated = self.service.save(
            symbol="RELIANCE",
            target_price=1700,
            priority="Medium",
        )
        self.assertEqual(updated.target_price, 1700)
        self.assertEqual(len(self.service.list_all()), 1)

        self.service.remove(saved.company_id)
        self.assertEqual(self.service.list_all(), [])

    def test_rejects_invalid_price(self):
        with self.assertRaises(ValueError):
            self.service.save(
                symbol="TCS",
                target_price=-1,
            )


if __name__ == "__main__":
    unittest.main()
