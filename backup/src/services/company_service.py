from src.models.company import Company
from src.dto.company_dto import CompanyDTO
from src.mapper.company_mapper import CompanyMapper


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

        provider_company = self.provider.get_company(symbol)

        if provider_company is None:
            raise ValueError(
                f"Unable to fetch company '{symbol}'"
            )

        company = (
            CompanyMapper.to_domain(provider_company)
            if isinstance(provider_company, CompanyDTO)
            else provider_company
        )

        self.repository.save(company)

        return company

    def ensure_company(
        self,
        symbol: str,
        isin: str | None = None,
    ) -> Company:

        company = None

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
