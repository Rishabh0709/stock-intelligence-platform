from sqlalchemy import insert, select, func

from src.database.tables import daily_prices
from src.models.daily_price import DailyPrice
from datetime import date

from abc import ABC, abstractmethod

class IPriceRepository(ABC):

    @abstractmethod
    def save(self, price: DailyPrice) -> None:
        pass

    @abstractmethod
    def bulk_save(
        self,
        prices: list[DailyPrice],
        ) -> None:
        pass
    
    @abstractmethod
    def get_latest_price_date(self, company_id: int):
        pass
    
    @abstractmethod
    def get_existing_dates(
        self,
        company_id: int,
        start_date,
        end_date,
        ) -> set[date]:
        pass
    
    @abstractmethod
    def get_prices_between(
        self,
        company_id: int,
        start_date,
        end_date,
        ):
        pass

    @abstractmethod
    def list_by_company(
        self,
        company_id: int,
        ) -> list[DailyPrice]:
        pass
    
    @abstractmethod
    def count(self, company_id: int | None = None) -> int:
        pass
        
    

        
            
            
            
class SQLitePriceRepository(IPriceRepository):

    def __init__(self, db_manager):
        self.db_manager = db_manager

    @property
    def engine(self):
        return self.db_manager.engine
    
    def save(
    self,
    price: DailyPrice,
        ) -> None:
        """
        Saves a single DailyPrice record.
        """

        self.bulk_save([price])
    
    def bulk_save(
        self,
        prices: list[DailyPrice],
        ) -> None:
        if not prices:
            return

        values = [price.to_dict() for price in prices]
        stmt = insert(daily_prices)

        with self.engine.begin() as conn:
            
            conn.execute(stmt, values,)

    
    
    def get_latest_price_date(self, company_id: int):
        stmt = (
        select(func.max(daily_prices.c.price_date))
        .where(daily_prices.c.company_id == company_id))

        with self.engine.connect() as conn:

            return conn.execute(stmt).scalar_one()

 
    
    def get_existing_dates(
        self,
        company_id: int,
        start_date,
        end_date,
        ) -> set[date]:
        stmt = (
        select(daily_prices.c.price_date)
        .where(daily_prices.c.company_id == company_id)
        .where(daily_prices.c.price_date >= start_date)
        .where(daily_prices.c.price_date <= end_date))
        
        with self.engine.connect() as conn:

            rows = conn.execute(stmt).fetchall()

        return { row.price_date for row in rows }
    
    
    
    def get_prices_between(
        self,
        company_id,
        start_date,
        end_date,
        ):

        stmt = (
            select(daily_prices)
            .where(daily_prices.c.company_id == company_id)
            .where(daily_prices.c.price_date.between(start_date, end_date,))
            .order_by(daily_prices.c.price_date)
        )

        with self.engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()

            return [
                DailyPrice(
                company_id=row.company_id,
                price_date=row.price_date,
                open_price=row.open,
                high_price=row.high,
                low_price=row.low,
                close_price=row.close,
                adjusted_close=row.adjusted_close,
                volume=row.volume,
                )
                for row in rows
            ]
            
    
    def list_by_company(
        self,
        company_id: int,
        ) -> list[DailyPrice]:
        stmt = (
        select(daily_prices)
        .where(daily_prices.c.company_id == company_id)
        .order_by(daily_prices.c.price_date))

        with self.engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()

            return [
                DailyPrice(
                company_id=row.company_id,
                price_date=row.price_date,
                open_price=row.open,
                high_price=row.high,
                low_price=row.low,
                close_price=row.close,
                adjusted_close=row.adjusted_close,
                volume=row.volume,
                )
                for row in rows
            ]
    

    def count(
        self,
        company_id: int | None = None,
        )-> int:

        stmt = select(func.count()).select_from(daily_prices)

        if company_id is not None:
            stmt = stmt.where(daily_prices.c.company_id == company_id)
            
        with self.engine.connect() as conn:
            return conn.execute(stmt).scalar_one()
            
