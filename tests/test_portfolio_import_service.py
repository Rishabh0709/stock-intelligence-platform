import unittest
from types import SimpleNamespace

from src.portfolio.dto.imported_holding import ImportedHolding
from src.portfolio.portfolio_import_service import PortfolioImportService


class CompanyServiceStub:
    def ensure_company(self, symbol, isin):
        return SimpleNamespace(id=7, symbol=symbol, isin=isin)


class PortfolioRepositoryStub:
    def __init__(self):
        self.holdings = []

    def upsert(self, holding):
        self.holdings.append(holding)


class PortfolioImportServiceTests(unittest.TestCase):
    def test_imports_parsed_holding(self):
        repository = PortfolioRepositoryStub()
        service = PortfolioImportService(CompanyServiceStub(), repository)
        service.parser = SimpleNamespace(
            parse=lambda _: [ImportedHolding("RELIANCE", "INE002A01018", 5, 1400)]
        )
        count = service.import_holdings("unused.csv")
        self.assertEqual(count, 1)
        self.assertEqual(repository.holdings[0].company_id, 7)
        self.assertEqual(repository.holdings[0].quantity, 5)


if __name__ == "__main__":
    unittest.main()
