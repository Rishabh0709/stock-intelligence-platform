from src.providers.yahoo_provider import YahooProvider
from src.repositories.company_repository import SQLiteCompanyRepository
from src.repositories.price_repository import SQLitePriceRepository
from src.services.price_sync_service import PriceSyncService
from src.services.company_service import CompanyService
from src.database.db_manager import DatabaseManager
from src.services.stock_explorer_service import StockExplorerService

class Bootstrap:

    def __init__(self):
        db = DatabaseManager()

        self.company_repository = SQLiteCompanyRepository(db)
        self.price_repository = SQLitePriceRepository(db)

        self.provider = YahooProvider()

        self.price_sync_service = PriceSyncService(
        provider=self.provider,
        company_repository=self.company_repository,
        price_repository=self.price_repository,
        )

        self.stock_explorer_service = StockExplorerService(
        provider=self.provider,
        company_repository=self.company_repository,
        price_repository=self.price_repository,
        price_sync_service=self.price_sync_service,
        )
        
        