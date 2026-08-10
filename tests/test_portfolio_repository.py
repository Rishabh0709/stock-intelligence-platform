import tempfile
import unittest
from pathlib import Path

from sqlalchemy import insert

from src.database.db_manager import DatabaseManager
from src.database.tables import companies
from src.models.portfolio_holding import PortfolioHolding
from src.repositories.portfolio_repository import SQLitePortfolioRepository


class PortfolioRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        path = Path(self.temp_dir.name) / "portfolio.db"
        self.db = DatabaseManager(f"sqlite:///{path}")
        with self.db.engine.begin() as connection:
            result = connection.execute(
                insert(companies).values(
                    symbol="RELIANCE",
                    company_name="Reliance Industries",
                    exchange="NSE",
                )
            )
            self.company_id = result.inserted_primary_key[0]
        self.repository = SQLitePortfolioRepository(self.db)

    def tearDown(self):
        self.db.engine.dispose()
        self.temp_dir.cleanup()

    def test_upsert_updates_one_holding(self):
        self.repository.upsert(PortfolioHolding(company_id=self.company_id, quantity=2, average_price=100))
        self.repository.upsert(PortfolioHolding(company_id=self.company_id, quantity=3, average_price=110))
        holding = self.repository.get(self.company_id)
        self.assertEqual(self.repository.count(), 1)
        self.assertEqual(holding.quantity, 3)
        self.assertEqual(holding.average_price, 110)


if __name__ == "__main__":
    unittest.main()
