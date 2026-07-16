from abc import ABC, abstractmethod

from sqlalchemy import select, insert, update, delete, func
from src.database.tables import companies, daily_prices
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
    
    @property
    def engine(self):
        return self.db_manager.engine

    def save(self, company: Company):

        
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
        with self.engine.begin() as conn:

            result = conn.execute(stmt)
        
        company.id = result.inserted_primary_key[0]
        return company

    def get_by_symbol(self, symbol: str):

        with self.db_manager.engine.connect() as conn:

            stmt = select(companies).where(companies.c.symbol == symbol)

            row = conn.execute(stmt).fetchone()

            if row is None:
                return None

            return Company(
                symbol=row.symbol,
                company_name=row.company_name,
                id = row.id,
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
                    id=row.id,
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
            
    def count(self) -> int:

        stmt = select(func.count()).select_from(companies)

        with self.engine.connect() as conn:
            return conn.execute(stmt).scalar_one()