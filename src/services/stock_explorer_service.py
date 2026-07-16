from src.models.company import Company
from src.providers.data_provider import IDataProvider
from src.repositories.company_repository import ICompanyRepository
from src.repositories.price_repository import IPriceRepository
from src.services.price_sync_service import PriceSyncService
from src.mapper.company_mapper import CompanyMapper

from src.models.daily_price import DailyPrice
from src.models.stock_data import StockData
from src.analytics.core.price_series import PriceSeries

class StockExplorerService:
    """
    Coordinates repositories and providers.

    The UI should interact only with this service.
    """

    def __init__(
        self,
        provider: IDataProvider,
        company_repository: ICompanyRepository,
        price_repository: IPriceRepository,
        price_sync_service: PriceSyncService,
    ):

        self.provider = provider
        self.company_repository = company_repository
        self.price_repository = price_repository
        self.price_sync_service = price_sync_service

    def get_company(self, symbol: str) -> Company:
        """
        Returns company information.
        Imports the company automatically if it does not exist.
        """
        symbol = symbol.upper().strip()
        company = self.company_repository.get_by_symbol(symbol)

        if company is not None:
            return company

        dto = self.provider.get_company(symbol)

        company = CompanyMapper.to_domain(dto)

        self.company_repository.save(company)

        return self.company_repository.get_by_symbol(symbol)
    
        
    def get_prices(self, symbol: str, sync: bool = True) -> list[DailyPrice]:

        company = self.get_company(symbol)
        if sync:    
            self.price_sync_service.sync(company)

        return self.price_repository.list_by_company(company.id)
        
    def get_stock(self, symbol: str) -> StockData:
        """
        Returns the complete stock object containing
        company information and historical price series.
        """

        company = self.get_company(symbol)

        prices = self.get_prices(symbol)

        series = PriceSeries(prices)

        return StockData(
            company=company,
            price_series=series,
            )