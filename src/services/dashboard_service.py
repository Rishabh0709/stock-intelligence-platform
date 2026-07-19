from pathlib import Path

from config.settings import DATABASE_PATH


class DashboardService:

    def __init__(
        self,
        company_repository,
        price_repository,
        portfolio_analyzer,
    ):
        self.company_repository = company_repository
        self.price_repository = price_repository
        self.portfolio_analyzer = portfolio_analyzer

    def get_dashboard_summary(self):

        db_path = Path(DATABASE_PATH)

        if db_path.exists():
            size_mb = round(
                db_path.stat().st_size / (1024 * 1024),
                2,
            )
        else:
            size_mb = 0

        portfolio = self.portfolio_analyzer.analyze()

        return {

            "companies": self.company_repository.count(),

            "price_records": self.price_repository.count(),

            "database_size": size_mb,

            "health_score": "--",

            "portfolio": portfolio,
        }