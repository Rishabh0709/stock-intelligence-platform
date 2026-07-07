from src.models.company import Company


class CompanyService:

    def __init__(self, repository):
        self.repository = repository

    def register_company(self, company: Company):

        if self.repository.exists(company.symbol):
            raise ValueError(
                f"Company '{company.symbol}' already exists."
            )

        self.repository.save(company)

    def get_company(self, symbol: str):

        return self.repository.get_by_symbol(symbol)

    def get_all_companies(self):

        return self.repository.list_all()