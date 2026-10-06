import unittest
from datetime import date

from sqlalchemy import create_engine

from src.database.tables import metadata
from src.dto.snapshot_dto import SnapshotDTO
from src.models.company import Company
from src.models.daily_price import DailyPrice
from src.repositories.company_repository import SQLiteCompanyRepository
from src.repositories.price_repository import SQLitePriceRepository
from src.services.stock_market_stats_service import StockMarketStatsService


class MemoryDatabase:
    def __init__(self):
        self.engine = create_engine("sqlite:///:memory:")
        metadata.create_all(self.engine)


class FakeCompanyService:
    def __init__(self, repository):
        self.repository = repository

    def get_company(self, symbol):
        return self.repository.get_by_symbol(symbol)

    def ensure_company(self, symbol):
        company = self.get_company(symbol)
        if company is None:
            company = self.repository.save(
                Company(
                    symbol=symbol,
                    company_name=f"{symbol} Limited",
                )
            )
        return company


class FakeProvider:
    def get_snapshot(self, symbol):
        return SnapshotDTO(
            symbol=symbol,
            current_price=410,
            fifty_two_week_high=425,
            fifty_two_week_low=240,
        )


class StockMarketStatsServiceTest(unittest.TestCase):
    def setUp(self):
        database = MemoryDatabase()
        self.addCleanup(database.engine.dispose)
        self.company_repository = SQLiteCompanyRepository(database)
        self.price_repository = SQLitePriceRepository(database)
        self.company_service = FakeCompanyService(self.company_repository)
        self.company = self.company_service.ensure_company("TEST")

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
                    company_id=self.company.id,
                    price_date=price_date,
                    open_price=value,
                    high_price=value,
                    low_price=value,
                    close_price=value,
                    adjusted_close=value,
                    volume=100,
                )
            )

    def test_calculates_shared_prices_ranges_and_returns(self):
        service = StockMarketStatsService(
            company_service=self.company_service,
            price_repository=self.price_repository,
        )

        stats = service.get_stats(
            "TEST",
            company_id=self.company.id,
        )

        self.assertEqual(stats.current_price, 400)
        self.assertEqual(stats.price_1d, 390)
        self.assertEqual(stats.price_1w, 350)
        self.assertEqual(stats.price_1m, 300)
        self.assertEqual(stats.price_6m, 250)
        self.assertEqual(stats.price_1y, 200)
        self.assertEqual(stats.price_3y, 100)
        self.assertEqual(stats.fifty_two_week_high, 400)
        self.assertEqual(stats.fifty_two_week_low, 250)
        self.assertEqual(stats.overall_high, 400)
        self.assertEqual(stats.overall_low, 100)
        self.assertEqual(stats.return_1d_percent, 2.56)
        self.assertEqual(stats.return_1y_percent, 100.0)

    def test_refresh_uses_live_price_and_provider_52_week_range(self):
        service = StockMarketStatsService(
            company_service=self.company_service,
            price_repository=self.price_repository,
            provider=FakeProvider(),
        )

        stats = service.get_stats(
            "TEST",
            company_id=self.company.id,
            refresh=True,
        )

        self.assertEqual(stats.current_price, 410)
        self.assertEqual(stats.fifty_two_week_high, 425)
        self.assertEqual(stats.fifty_two_week_low, 240)
        self.assertEqual(stats.return_1d_percent, 5.13)


if __name__ == "__main__":
    unittest.main()
