from pathlib import Path

from src.models.portfolio_holding import PortfolioHolding
from src.portfolio.importer.zerodha_holding_parser import (
    ZerodhaHoldingParser,
)
from src.services.company_service import CompanyService
from src.repositories.portfolio_repository import (
    SQLitePortfolioRepository,
)

from src.services.price_sync_service import PriceSyncService

class PortfolioImportService:
    """
    Imports holdings from a Zerodha Holdings CSV into the portfolio.
    Automatically creates missing companies.
    """

    def __init__(
        self,
        company_service: CompanyService,
        portfolio_repository: SQLitePortfolioRepository,
        price_sync_service:PriceSyncService
    ):
        self.company_service = company_service
        self.portfolio_repository = portfolio_repository
        self.parser = ZerodhaHoldingParser()
        self.price_sync_service = price_sync_service

    def import_holdings(
        self,
        file_path: str | Path,
    ) -> int:

        print(">>> USING NEW PortfolioImportService <<<")
        print(__file__)
        imported_holdings = self.parser.parse(file_path)

        imported_count = 0

        for imported in imported_holdings:

            try:

                company = self.company_service.ensure_company(
                    symbol=imported.symbol,
                    isin=imported.isin,
                )
                print(f"Downloading prices for {company.symbol}...")
                result = self.price_sync_service.sync(company)
                print(
                    f"{company.symbol}: downloaded={result.downloaded_records}, "
                    f"inserted={result.inserted_records}"
                    )

            except Exception as ex:

                print(
                    f"[WARNING] Unable to import "
                    f"{imported.symbol}: {ex}"
                )

                continue

            holding = PortfolioHolding(
                company_id=company.id,
                quantity=imported.quantity,
                average_price=imported.average_price,
            )

            self.portfolio_repository.upsert(
                holding,
            )

            imported_count += 1

        return imported_count