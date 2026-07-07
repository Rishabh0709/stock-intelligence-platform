from src.collectors.yahoo_collector import YahooCollector
from src.repositories.company_repository import SQLiteCompanyRepository
from src.services.company_service import CompanyService
from src.database.db_manager import DatabaseManager


class CLI:

    def __init__(self):

        db = DatabaseManager()
        db.create_tables()

        repository = SQLiteCompanyRepository(db)
        collector = YahooCollector()

        self.service = CompanyService(
            repository,
            collector
        )

    def import_company(self, symbol):

        company = self.service.import_company(symbol)

        print(company)

    def list_companies(self):

        companies = self.service.get_all_companies()

        for company in companies:
            print(company.symbol, "-", company.company_name)

    def search_company(self, symbol):

        company = self.service.get_company(symbol)

        print(company)