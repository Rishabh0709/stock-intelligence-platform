from datetime import date, timedelta

from config.settings import DEFAULT_HISTORY_YEARS, PRICE_SYNC_BUFFER_DAYS
from src.dto.sync_result_dto import SyncResultDTO
from src.mapper.daily_price_mapper import DailyPriceMapper
from src.models.company import Company
from src.providers.price_provider import IPriceProvider
from src.repositories.company_repository import ICompanyRepository
from src.repositories.price_repository import IPriceRepository


class PriceSyncService:
    def __init__(
        self,
        provider: IPriceProvider,
        price_repository: IPriceRepository,
        company_repository: ICompanyRepository,
    ):
        self.provider = provider
        self.price_repository = price_repository
        self.company_repository = company_repository

    def _calculate_sync_start_date(self, latest_date) -> date:
        if latest_date is None:
            return date.today() - timedelta(days=365 * DEFAULT_HISTORY_YEARS)
        return latest_date - timedelta(days=PRICE_SYNC_BUFFER_DAYS)

    def sync(self, company: Company) -> SyncResultDTO:
        """Reconcile the provider buffer with locally stored candles."""
        latest_date = self.price_repository.get_latest_price_date(company.id)
        start_date = self._calculate_sync_start_date(latest_date)
        provider_prices = self.provider.get_price_history(
            company.symbol,
            start_date,
            date.today(),
        )
        prices = sorted(
            DailyPriceMapper.to_domain_list(provider_prices, company.id),
            key=lambda item: item.price_date,
        )

        result = self.price_repository.bulk_upsert(
            prices,
            provider=self.provider.__class__.__name__,
        )
        latest_price_date = prices[-1].price_date if prices else latest_date

        return SyncResultDTO(
            company_symbol=company.symbol,
            downloaded_records=len(provider_prices),
            inserted_records=result.inserted,
            updated_records=result.updated,
            skipped_records=result.unchanged,
            latest_price_date=latest_price_date,
        )
