import unittest
from datetime import date

from sqlalchemy import create_engine

from src.database.tables import metadata
from src.models.company import Company
from src.models.daily_price import DailyPrice
from src.repositories.company_repository import SQLiteCompanyRepository
from src.repositories.price_repository import SQLitePriceRepository
from src.repositories.watchlist_repository import SQLiteWatchlistRepository
from src.services.stock_market_stats_service import StockMarketStatsService
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

    def get_company(self, symbol):
        return self.repository.get_by_symbol(symbol)


class WatchlistServiceTest(unittest.TestCase):
    def setUp(self):
        database = MemoryDatabase()
        self.addCleanup(database.engine.dispose)
        self.company_repository = SQLiteCompanyRepository(database)
        self.price_repository = SQLitePriceRepository(database)
        self.repository = SQLiteWatchlistRepository(database)
        company_service = FakeCompanyService(self.company_repository)
        market_stats_service = StockMarketStatsService(
            company_service=company_service,
            price_repository=self.price_repository,
        )
        self.service = WatchlistService(
            repository=self.repository,
            company_service=company_service,
            market_stats_service=market_stats_service,
        )

    def test_save_update_overview_and_remove(self):
        saved = self.service.save(
            symbol="RELIANCE",
            target_price=1650,
            alert_price=1400,
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
        self.assertEqual(overview.overall_high, 1500)
        self.assertEqual(overview.overall_low, 1500)

        updated = self.service.save(
            symbol="RELIANCE",
            target_price=1700,
            alert_price=1450,
        )
        self.assertEqual(updated.target_price, 1700)
        self.assertEqual(updated.alert_price, 1450)
        self.assertEqual(len(self.service.list_all()), 1)

        self.service.remove(saved.company_id)
        self.assertEqual(self.service.list_all(), [])

    def test_rejects_invalid_price(self):
        with self.assertRaises(ValueError):
            self.service.save(
                symbol="TCS",
                target_price=-1,
                alert_price=100,
            )

        with self.assertRaises(ValueError):
            self.service.save(
                symbol="TCS",
                target_price=100,
                alert_price=None,
            )

    def test_populates_lookback_high_and_low_prices(self):
        saved = self.service.save(
            symbol="TCS",
            target_price=5000,
            alert_price=3500,
        )
        samples = [
            (date(2023, 7, 28), 100),
            (date(2025, 7, 28), 200),
            (date(2026, 1, 26), 250),
            (date(2026, 6, 26), 300),
            (date(2026, 7, 21), 350),
            (date(2026, 7, 30), 390),
            (date(2026, 7, 31), 400),
        ]
        for price_date, value in samples:
            self.price_repository.save(
                DailyPrice(
                    company_id=saved.company_id,
                    price_date=price_date,
                    open_price=value,
                    high_price=value,
                    low_price=value,
                    close_price=value,
                    adjusted_close=value,
                    volume=100,
                )
            )

        overview = self.service.get_overview()[0]
        self.assertEqual(overview.price_1d, 390)
        self.assertEqual(overview.price_1w, 350)
        self.assertEqual(overview.price_1m, 300)
        self.assertEqual(overview.price_6m, 250)
        self.assertEqual(overview.price_1y, 200)
        self.assertEqual(overview.price_3y, 100)
        self.assertEqual(overview.fifty_two_week_high, 400)
        self.assertEqual(overview.fifty_two_week_low, 250)
        self.assertEqual(overview.overall_high, 400)
        self.assertEqual(overview.overall_low, 100)


if __name__ == "__main__":
    unittest.main()
