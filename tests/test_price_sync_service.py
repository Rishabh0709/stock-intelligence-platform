import unittest
from datetime import date

from src.dto.daily_price_dto import DailyPriceDTO
from src.models.company import Company
from src.repositories.price_repository import PriceUpsertResult
from src.services.price_sync_service import PriceSyncService


class ProviderStub:
    def get_price_history(self, symbol, start_date, end_date):
        return [
            DailyPriceDTO(
                price_date=date(2026, 8, 8),
                open_price=99,
                high_price=102,
                low_price=98,
                close_price=100,
                adjusted_close=100,
                volume=1000,
            )
        ]


class PriceRepositoryStub:
    def get_latest_price_date(self, company_id):
        return date(2026, 8, 7)

    def bulk_upsert(self, prices, *, provider):
        self.prices = prices
        self.provider = provider
        return PriceUpsertResult(inserted=0, updated=1, unchanged=0)


class PriceSyncServiceTests(unittest.TestCase):
    def test_reports_corrected_provider_candle(self):
        repository = PriceRepositoryStub()
        service = PriceSyncService(
            provider=ProviderStub(),
            price_repository=repository,
            company_repository=object(),
        )
        company = Company(
            id=1,
            symbol="RELIANCE",
            company_name="Reliance Industries",
            exchange="NSE",
        )

        result = service.sync(company)

        self.assertEqual(result.downloaded_records, 1)
        self.assertEqual(result.updated_records, 1)
        self.assertEqual(result.inserted_records, 0)
        self.assertEqual(result.skipped_records, 0)
        self.assertEqual(result.latest_price_date, date(2026, 8, 8))
        self.assertEqual(repository.provider, "ProviderStub")


if __name__ == "__main__":
    unittest.main()
