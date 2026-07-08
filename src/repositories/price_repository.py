from sqlalchemy import insert, select, func

from src.database.tables import daily_prices
from src.models.daily_price import DailyPrice


class SQLitePriceRepository:

    def __init__(self, db_manager):
        self.db_manager = db_manager

    @property
    def engine(self):
        return self.db_manager.engine

    def save_prices(self, prices: list[DailyPrice]):

        if not prices:
            return 0

        rows = []

        for price in prices:

            rows.append(
                {
                    "company_id": price.company_id,
                    "price_date": price.price_date,
                    "open": price.open,
                    "high": price.high,
                    "low": price.low,
                    "close": price.close,
                    "adjusted_close": price.adjusted_close,
                    "volume": price.volume,
                }
            )

        with self.engine.begin() as conn:

            conn.execute(
                insert(daily_prices),
                rows,
            )

        return len(rows)

    def get_latest_date(self, company_id):

        stmt = (
            select(func.max(daily_prices.c.price_date))
            .where(daily_prices.c.company_id == company_id)
        )

        with self.engine.connect() as conn:
            return conn.execute(stmt).scalar()

    def get_prices(self, company_id):

        stmt = (
            select(daily_prices)
            .where(daily_prices.c.company_id == company_id)
            .order_by(daily_prices.c.price_date)
        )

        with self.engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def get_prices_between(
        self,
        company_id,
        start_date,
        end_date,
    ):

        stmt = (
            select(daily_prices)
            .where(daily_prices.c.company_id == company_id)
            .where(
                daily_prices.c.price_date.between(
                    start_date,
                    end_date,
                )
            )
            .order_by(daily_prices.c.price_date)
        )

        with self.engine.connect() as conn:
            return conn.execute(stmt).fetchall()

    def count(self) -> int:

        stmt = select(func.count()).select_from(daily_prices)

        with self.engine.connect() as conn:
            return conn.execute(stmt).scalar_one()