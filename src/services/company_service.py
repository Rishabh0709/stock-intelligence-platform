from src.models.company import Company


class CompanyService:

    def __init__(
        self,
        repository,
        provider,
    ):
        self.repository = repository
        self.provider = provider

    def upsert_company(
        self,
        company: Company,
    ):

        existing = self.repository.get_by_symbol(
            company.symbol,
        )

        if existing is not None:
            return existing

        self.repository.save(company)

        return company

    def import_company(
        self,
        symbol: str,
    ) -> Company:

        existing = self.repository.get_by_symbol(
            symbol,
        )

        if existing is not None:
            return existing

        dto = self.provider.get_company(symbol)

        if dto is None:
            raise ValueError(
                f"Unable to fetch company '{symbol}'"
            )

        company = Company(
            symbol=dto.symbol,
            company_name=dto.company_name,
            exchange=dto.exchange,
            isin=dto.isin,
            sector=dto.sector,
            industry=dto.industry,
            country=dto.country or "India",
            currency=dto.currency or "INR",
            website=dto.website,
            business_description=dto.business_description,
            )

        self.repository.save(company)

        return self.repository.get_by_symbol(symbol)

    def ensure_company(
        self,
        symbol: str,
        isin: str | None = None,
    ) -> Company:

        company = None
        print(f"ensure_company() called for {symbol}")
        if isin:

            company = self.repository.get_by_isin(
                isin,
            )

        if company is None:

            company = self.repository.get_by_symbol(
                symbol,
            )

            if company is not None and isin:

                if (
                    company.isin is None
                    or company.isin == ""
                ):
                    self.repository.update_isin(
                        company.id,
                        isin,
                    )

                    company = self.repository.get_by_symbol(
                        symbol,
                    )

        if company is None:

            company = self.import_company(
                symbol,
            )

            if (
                isin
                and company.isin != isin
            ):
                self.repository.update_isin(
                    company.id,
                    isin,
                )

                company = self.repository.get_by_symbol(
                    symbol,
                )

        return company

    def get_company(
        self,
        symbol: str,
    ):

        return self.repository.get_by_symbol(
            symbol,
        )

    def get_all_companies(self):

        return self.repository.list_all()