from abc import ABC, abstractmethod

from sqlalchemy import insert, select

from src.database.schema import companies
from src.models.company import Company


class ICompanyRepository(ABC):

    @abstractmethod
    def save(self, company: Company):
        pass

    @abstractmethod
    def get_by_symbol(self, symbol: str):
        pass

    @abstractmethod
    def exists(self, symbol: str):
        pass

    @abstractmethod
    def list_all(self):
        pass


class SQLiteCompanyRepository(ICompanyRepository):

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def save(self, company: Company):

        with self.db_manager.engine.begin() as conn:

            stmt = insert(companies).values(
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
                created_at=company.created_at,
            )

            conn.execute(stmt)

    def get_by_symbol(self, symbol: str):

        with self.db_manager.engine.connect() as conn:

            stmt = select(companies).where(companies.c.symbol == symbol)

            row = conn.execute(stmt).fetchone()

            if row is None:
                return None

            return Company(
                symbol=row.symbol,
                company_name=row.company_name,
                exchange=row.exchange,
                isin=row.isin,
                sector=row.sector,
                industry=row.industry,
                country=row.country,
                currency=row.currency,
                website=row.website,
                business_description=row.business_description,
                created_at=row.created_at,
            )

    def exists(self, symbol: str):

        return self.get_by_symbol(symbol) is not None

    def list_all(self):

        with self.db_manager.engine.connect() as conn:

            rows = conn.execute(select(companies)).fetchall()

            return [
                Company(
                    symbol=row.symbol,
                    company_name=row.company_name,
                    exchange=row.exchange,
                    isin=row.isin,
                    sector=row.sector,
                    industry=row.industry,
                    country=row.country,
                    currency=row.currency,
                    website=row.website,
                    business_description=row.business_description,
                    created_at=row.created_at,
                )
                for row in rows
            ]