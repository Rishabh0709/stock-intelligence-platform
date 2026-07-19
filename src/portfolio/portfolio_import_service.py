from pathlib import Path

from src.models.portfolio_holding import PortfolioHolding
from src.portfolio.importer.zerodha_holding_parser import (
    ZerodhaHoldingParser,
)
from src.repositories.company_repository import (
    SQLiteCompanyRepository,
)
from src.repositories.portfolio_repository import (
    SQLitePortfolioRepository,
)


class PortfolioImportService:
    """
    Imports holdings from a Zerodha Holdings CSV into the portfolio.
    """

    def __init__(
        self,
        company_repository: SQLiteCompanyRepository,
        portfolio_repository: SQLitePortfolioRepository,
    ):
        self.company_repository = company_repository
        self.portfolio_repository = portfolio_repository
        self.parser = ZerodhaHoldingParser()

    def import_holdings(
        self,
        file_path: str | Path,
    ) -> int:

        imported_holdings = self.parser.parse(file_path)

        imported_count = 0

        for imported in imported_holdings:

            company = self.company_repository.get_by_isin(
                imported.isin,
            )

            if company is None:

                company = self.company_repository.get_by_symbol(imported.symbol,)

                if company is not None:

                    self.company_repository.update_isin(company.id, imported.isin,)
                    print(f"Updated ISIN for {company.symbol}: {imported.isin}")

                    company = self.company_repository.get_by_isin(imported.isin,)
            
            if company is None:
                print(
                    f"[WARNING] Company not found for "
                    f"{imported.symbol} ({imported.isin})"
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