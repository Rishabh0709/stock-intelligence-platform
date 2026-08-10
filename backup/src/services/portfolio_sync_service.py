from pathlib import Path

from src.portfolio.importer.zerodha_holding_parser import (
    ZerodhaHoldingParser,
)

from src.portfolio.dto.sync_result_dto import SyncResultDTO

from src.repositories.interfaces.i_company_repository import (
    ICompanyRepository,
)

from src.services.price_sync_service import PriceSyncService


class PortfolioSyncService:
    """
    Synchronizes all companies present in a portfolio.

    Responsibilities:
    - Parse holdings file.
    - Ensure every company exists.
    - Download/update historical prices.
    """

    def __init__(
        self,
        parser: ZerodhaHoldingParser,
        company_repository: ICompanyRepository,
        price_sync_service: PriceSyncService,
    ):
        self.parser = parser
        self.company_repository = company_repository
        self.price_sync_service = price_sync_service

    def sync(
        self,
        file_path: str | Path,
    ) -> list[SyncResultDTO]:

        results = []

        for holding in holdings:

            result = self.price_sync_service.sync(holding.symbol,)

            results.append(result)

        return results