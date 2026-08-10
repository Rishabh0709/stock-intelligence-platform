from src.dto.company_dto import CompanyDTO
from src.models.company import Company


class CompanyMapper:
    """
    Maps between CompanyDTO and Company domain model.
    """

    @staticmethod
    def to_domain(dto: CompanyDTO) -> Company:
        return Company(
            symbol=dto.symbol,
            company_name=dto.company_name,
            exchange=dto.exchange,
            isin=dto.isin,
            sector=dto.sector,
            industry=dto.industry,
            country=dto.country,
            currency=dto.currency,
            website=dto.website,
            business_description=dto.business_description,
        )

    @staticmethod
    def to_dto(company: Company) -> CompanyDTO:
        return CompanyDTO(
            symbol=company.symbol,
            company_name=company.company_name,
            exchange=company.exchange,
            isin=company.isin,
            sector=company.sector,
            industry=company.industry,
            country=company.country,
            currency=company.currency,
            website=company.website,
            business_description=company.business_description,
        )