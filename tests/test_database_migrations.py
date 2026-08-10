import sqlite3
import tempfile
import unittest
from pathlib import Path

from sqlalchemy import inspect, text

from src.database.db_manager import DatabaseManager


class DatabaseMigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "migration.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    @property
    def database_url(self):
        return f"sqlite:///{self.database_path}"

    def test_new_database_is_upgraded_to_head(self):
        db = DatabaseManager(self.database_url)
        try:
            inspector = inspect(db.engine)
            self.assertIn("alembic_version", inspector.get_table_names())
            self.assertIn("watchlist_items", inspector.get_table_names())
            columns = {item["name"] for item in inspector.get_columns("daily_prices")}
            self.assertTrue(
                {"provider", "downloaded_at", "last_verified_at"}.issubset(columns)
            )
        finally:
            db.engine.dispose()

    def test_existing_price_data_survives_schema_adoption(self):
        connection = sqlite3.connect(self.database_path)
        connection.executescript(
            """
            CREATE TABLE companies (
                id INTEGER PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL UNIQUE,
                company_name VARCHAR(255) NOT NULL,
                exchange VARCHAR(20) NOT NULL,
                isin VARCHAR(20), sector VARCHAR(100), industry VARCHAR(100),
                country VARCHAR(50), currency VARCHAR(10), website VARCHAR(255),
                business_description TEXT, created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE daily_prices (
                id INTEGER PRIMARY KEY,
                company_id INTEGER NOT NULL REFERENCES companies(id),
                price_date DATE NOT NULL,
                open FLOAT, high FLOAT, low FLOAT, close FLOAT,
                adjusted_close FLOAT, volume BIGINT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_company_price_date UNIQUE (company_id, price_date)
            );
            INSERT INTO companies (id, symbol, company_name, exchange)
                VALUES (1, 'RELIANCE', 'Reliance Industries', 'NSE');
            INSERT INTO daily_prices
                (company_id, price_date, open, high, low, close, adjusted_close, volume)
                VALUES (1, '2026-08-08', 99, 102, 98, 100, 100, 1000);
            """
        )
        connection.commit()
        connection.close()

        db = DatabaseManager(self.database_url)
        try:
            with db.engine.connect() as migrated:
                count = migrated.execute(text("SELECT COUNT(*) FROM daily_prices")).scalar_one()
                version = migrated.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
            self.assertEqual(count, 1)
            self.assertEqual(version, "0002_price_verification_metadata")
        finally:
            db.engine.dispose()


if __name__ == "__main__":
    unittest.main()
