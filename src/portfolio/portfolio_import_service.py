from pathlib import Path

from src.models.portfolio_holding import PortfolioHolding
from src.portfolio.importer.zerodha_holding_parser import (
    ZerodhaHoldingParser,
)
from src.services.company_service import CompanyService
from src.repositories.portfolio_repository import (
    SQLitePortfolioRepository,
)


class PortfolioImportService:
    """
    Imports holdings from a Zerodha Holdings CSV into the portfolio.
    Automatically creates missing companies.
    """

    def __init__(
        self,
        company_service: CompanyService,
        portfolio_repository: SQLitePortfolioRepository,
    ):
        self.company_service = company_service
        self.portfolio_repository = portfolio_repository
        self.parser = ZerodhaHoldingParser()

    def import_holdings(
        self,
        file_path: str | Path,
    ) -> int:

        imported_holdings = self.parser.parse(file_path)

        imported_count = 0

        for imported in imported_holdings:

            try:

                company = self.company_service.ensure_company(
                    symbol=imported.symbol,
                    isin=imported.isin,
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