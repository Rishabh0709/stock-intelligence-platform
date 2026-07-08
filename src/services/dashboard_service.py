from pathlib import Path

from config.settings import DATABASE_PATH
from src.database.db_manager import DatabaseManager
from src.repositories.company_repository import SQLiteCompanyRepository
from src.repositories.price_repository import SQLitePriceRepository


class DashboardService:

    def __init__(self, company_repository, price_repository):
        self.company_repository = company_repository
        self.price_repository = price_repository

    def get_summary(self):

        db_path = Path(DATABASE_PATH)

        if db_path.exists():
            size_mb = round(db_path.stat().st_size / (1024 * 1024), 2)
        else:
            size_mb = 0

        return {
            "companies": self.company_repository.count(),
            "price_records": self.price_repository.count(),
            "database_size": size_mb,
            "portfolio_value": 0,
            "health_score": "--",
        }