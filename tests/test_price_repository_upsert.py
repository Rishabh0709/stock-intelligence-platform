import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from sqlalchemy import insert, select

from src.database.db_manager import DatabaseManager
from src.database.tables import companies, daily_prices
from src.models.daily_price import DailyPrice
from src.repositories.price_repository import SQLitePriceRepository


class PriceRepositoryUpsertTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "prices.db"
        self.db = DatabaseManager(f"sqlite:///{database_path}")
        with self.db.engine.begin() as connection:
            result = connection.execute(
                insert(companies).values(
                    symbol="RELIANCE",
                    company_name="Reliance Industries",
                    exchange="NSE",
                )
            )
            self.company_id = result.inserted_primary_key[0]
        self.repository = SQLitePriceRepository(self.db)
        self.verified_at = datetime(2026, 8, 10, 12, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.db.engine.dispose()
        self.temp_dir.cleanup()

    def price(self, close: float, *, volume: int = 1000) -> DailyPrice:
        return DailyPrice(
            company_id=self.company_id,
            price_date=date(2026, 8, 8),
            open_price=close - 1,
            high_price=close + 2,
            low_price=close - 2,
            close_price=close,
            adjusted_close=close,
            volume=volume,
        )

    def test_inserts_new_candle_with_provenance(self):
        result = self.repository.bulk_upsert(
            [self.price(100)],
            provider="YahooProvider",
            verified_at=self.verified_at,
        )

        self.assertEqual((result.inserted, result.updated, result.unchanged), (1, 0, 0))
        with self.db.engine.connect() as connection:
            row = connection.execute(select(daily_prices)).mappings().one()
        self.assertEqual(row["provider"], "YahooProvider")
        self.assertEqual(row["close"], 100)
        self.assertIsNotNone(row["last_verified_at"])

    def test_updates_corrected_candle_without_creating_duplicate(self):
        self.repository.bulk_upsert(
            [self.price(100)], provider="YahooProvider", verified_at=self.verified_at
        )

        result = self.repository.bulk_upsert(
            [self.price(103, volume=1200)],
            provider="YahooProvider",
            verified_at=self.verified_at,
        )

        self.assertEqual((result.inserted, result.updated, result.unchanged), (0, 1, 0))
        self.assertEqual(self.repository.count(self.company_id), 1)
        stored = self.repository.list_by_company(self.company_id)[0]
        self.assertEqual(stored.close_price, 103)
        self.assertEqual(stored.volume, 1200)

    def test_counts_identical_candle_as_unchanged(self):
        candle = self.price(100)
        self.repository.bulk_upsert(
            [candle], provider="YahooProvider", verified_at=self.verified_at
        )

        result = self.repository.bulk_upsert(
            [candle], provider="YahooProvider", verified_at=self.verified_at
        )

        self.assertEqual((result.inserted, result.updated, result.unchanged), (0, 0, 1))

    def test_last_duplicate_in_batch_wins(self):
        result = self.repository.bulk_upsert(
            [self.price(100), self.price(105)],
            provider="YahooProvider",
            verified_at=self.verified_at,
        )

        self.assertEqual(result.processed, 1)
        self.assertEqual(self.repository.list_by_company(self.company_id)[0].close_price, 105)


if __name__ == "__main__":
    unittest.main()
