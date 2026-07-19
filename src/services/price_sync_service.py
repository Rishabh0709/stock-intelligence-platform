from datetime import date, timedelta

from config.settings import (
    DEFAULT_HISTORY_YEARS,
    PRICE_SYNC_BUFFER_DAYS,
)

from src.mapper.daily_price_mapper import DailyPriceMapper
from src.dto.sync_result_dto import SyncResultDTO
from src.models.company import Company
from src.providers.price_provider import IPriceProvider
from src.repositories.price_repository import IPriceRepository
from src.repositories.company_repository import ICompanyRepository
from src.models.daily_price import DailyPrice



class PriceSyncService:

    def __init__(
        self,
        provider: IPriceProvider,
        price_repository: IPriceRepository,
        company_repository: ICompanyRepository
    ):

        self.provider = provider
        self.price_repository = price_repository
        self.company_repository = company_repository
        
    def _calculate_sync_start_date(
        self,
        latest_date,
    ) -> date:
        """
       Determines the date from which prices should be downloaded.
       
        """

        if latest_date is None:

            return date.today() - timedelta(
                days=365 * DEFAULT_HISTORY_YEARS
            )
        
        return latest_date - timedelta(
            days=PRICE_SYNC_BUFFER_DAYS
        )
        
    def _filter_new_prices(
        self,
        company_id: int,
        prices: list,
    ) -> list[DailyPrice]:
        """
        Removes prices already present in the database.
        """

        if not prices:
            return []

        existing_dates = self.price_repository.get_existing_dates(
            company_id,
            prices[0].price_date,
            prices[-1].price_date,
        )

        return [
            price
            for price in prices
            if price.price_date not in existing_dates
        ]
        

    def sync(
        self,
        company: Company,
        ) -> SyncResultDTO:
        """
        Synchronizes historical prices for a company.
        """

        latest_date = self.price_repository.get_latest_price_date(company.id)

        start_date = self._calculate_sync_start_date(latest_date)

        provider_prices = self.provider.get_price_history(company.symbol, start_date, date.today())

        prices = DailyPriceMapper.to_domain_list(provider_prices, company.id)

        new_prices = self._filter_new_prices(company.id, prices)

        self.price_repository.bulk_save(new_prices)

        skipped_records = (len(provider_prices) - len(new_prices))
        
        latest_price_date = (new_prices[-1].price_date if new_prices else latest_date)

        return SyncResultDTO(
            company_symbol=company.symbol,
            downloaded_records=len(provider_prices),
            inserted_records=len(new_prices),
            skipped_records = skipped_records,
            latest_price_date=latest_price_date,
        )