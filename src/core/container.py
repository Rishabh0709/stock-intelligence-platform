from src.database.db_manager import DatabaseManager

from src.repositories.company_repository import SQLiteCompanyRepository

from src.repositories.price_repository import SQLitePriceRepository

from src.providers.yahoo_provider import YahooProvider

from src.services.company_service import CompanyService

from src.services.stock_explorer_service import StockExplorerService


db_manager = DatabaseManager()


company_repository = SQLiteCompanyRepository(db_manager)

price_repository = SQLitePriceRepository(db_manager)


provider = YahooProvider()

company_service = CompanyService(
    company_repository,
    yahoo_collector
)

stock_service = StockExplorerService(
    yahoo_collector
)