from src.models.company import Company


class CompanyService:

    def __init__(self, repository, collector):
        self.repository = repository
        self.collector = collector
        
    #update if exists, insert if not
    def upsert_company(self, company: Company):

        if self.repository.exists(company.symbol):
            raise ValueError(
                f"Company '{company.symbol}' already exists."
            )

        self.repository.save(company)

    def import_company(self, symbol: str):

        company = self.collector.get_company(symbol)

        if company is None:
            raise ValueError(f"Unable to fetch company '{symbol}'")

        if self.repository.exists(symbol):
            print(f"'{symbol}' already exists in database.")
            return self.repository.get_by_symbol(symbol)

        self.repository.save(company)

        print(f"'{symbol}' imported successfully.")

        return company

    def get_company(self, symbol: str):
        return self.repository.get_by_symbol(symbol)

    def get_all_companies(self):
        return self.repository.list_all()