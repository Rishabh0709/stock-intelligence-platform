from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Iterable

from sqlalchemy import func, insert, select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from src.database.tables import daily_prices
from src.models.daily_price import DailyPrice


@dataclass(frozen=True, slots=True)
class PriceUpsertResult:
    inserted: int = 0
    updated: int = 0
    unchanged: int = 0

    @property
    def processed(self) -> int:
        return self.inserted + self.updated + self.unchanged


class IPriceRepository(ABC):
    @abstractmethod
    def save(self, price: DailyPrice) -> None:
        ...

    @abstractmethod
    def bulk_save(self, prices: list[DailyPrice]) -> None:
        ...

    @abstractmethod
    def bulk_upsert(
        self,
        prices: list[DailyPrice],
        *,
        provider: str,
        verified_at: datetime | None = None,
    ) -> PriceUpsertResult:
        ...

    @abstractmethod
    def get_latest_price_date(self, company_id: int):
        ...

    @abstractmethod
    def get_existing_dates(
        self,
        company_id: int,
        start_date,
        end_date,
    ) -> set[date]:
        ...

    @abstractmethod
    def get_prices_between(self, company_id: int, start_date, end_date):
        ...

    @abstractmethod
    def list_by_company(self, company_id: int) -> list[DailyPrice]:
        ...

    @abstractmethod
    def count(self, company_id: int | None = None) -> int:
        ...


class SQLitePriceRepository(IPriceRepository):
    _PRICE_FIELDS = (
        "open",
        "high",
        "low",
        "close",
        "adjusted_close",
        "volume",
    )

    def __init__(self, db_manager):
        self.db_manager = db_manager

    @property
    def engine(self):
        return self.db_manager.engine

    def save(self, price: DailyPrice) -> None:
        self.bulk_save([price])

    def bulk_save(self, prices: list[DailyPrice]) -> None:
        """Insert prices and retain the legacy duplicate-error behaviour."""
        if not prices:
            return
        with self.engine.begin() as conn:
            conn.execute(insert(daily_prices), [price.to_dict() for price in prices])

    @staticmethod
    def _deduplicate(prices: Iterable[DailyPrice]) -> list[DailyPrice]:
        by_key: dict[tuple[int, date], DailyPrice] = {}
        for price in prices:
            by_key[(price.company_id, price.price_date)] = price
        return list(by_key.values())

    @classmethod
    def _price_changed(cls, existing, incoming: dict) -> bool:
        return any(existing[field] != incoming[field] for field in cls._PRICE_FIELDS)

    def bulk_upsert(
        self,
        prices: list[DailyPrice],
        *,
        provider: str,
        verified_at: datetime | None = None,
    ) -> PriceUpsertResult:
        """Insert new candles and replace corrected values atomically.

        The synchronization buffer is intentionally re-verified on every run.
        Unchanged candles still receive a new ``last_verified_at`` timestamp,
        while ``created_at`` remains untouched.
        """
        unique_prices = self._deduplicate(prices)
        if not unique_prices:
            return PriceUpsertResult()

        company_ids = {price.company_id for price in unique_prices}
        start_date = min(price.price_date for price in unique_prices)
        end_date = max(price.price_date for price in unique_prices)
        verified_at = verified_at or datetime.now(timezone.utc)

        lookup = (
            select(daily_prices)
            .where(daily_prices.c.company_id.in_(company_ids))
            .where(daily_prices.c.price_date.between(start_date, end_date))
        )

        with self.engine.begin() as conn:
            existing_rows = {
                (row["company_id"], row["price_date"]): row
                for row in conn.execute(lookup).mappings()
            }

            inserted_count = 0
            updated_count = 0
            unchanged_count = 0
            values = []
            for price in unique_prices:
                value = price.to_dict()
                value.update(
                    provider=provider,
                    downloaded_at=verified_at,
                    last_verified_at=verified_at,
                )
                existing = existing_rows.get((price.company_id, price.price_date))
                if existing is None:
                    inserted_count += 1
                elif self._price_changed(existing, value):
                    updated_count += 1
                else:
                    unchanged_count += 1
                values.append(value)

            statement = sqlite_insert(daily_prices).values(values)
            excluded = statement.excluded
            statement = statement.on_conflict_do_update(
                index_elements=["company_id", "price_date"],
                set_={
                    field: getattr(excluded, field)
                    for field in self._PRICE_FIELDS
                }
                | {
                    "provider": excluded.provider,
                    "downloaded_at": excluded.downloaded_at,
                    "last_verified_at": excluded.last_verified_at,
                },
            )
            conn.execute(statement)

        return PriceUpsertResult(
            inserted=inserted_count,
            updated=updated_count,
            unchanged=unchanged_count,
        )

    def get_latest_price_date(self, company_id: int):
        statement = select(func.max(daily_prices.c.price_date)).where(
            daily_prices.c.company_id == company_id
        )
        with self.engine.connect() as conn:
            return conn.execute(statement).scalar_one()

    def get_existing_dates(
        self,
        company_id: int,
        start_date,
        end_date,
    ) -> set[date]:
        statement = (
            select(daily_prices.c.price_date)
            .where(daily_prices.c.company_id == company_id)
            .where(daily_prices.c.price_date >= start_date)
            .where(daily_prices.c.price_date <= end_date)
        )
        with self.engine.connect() as conn:
            rows = conn.execute(statement).fetchall()
        return {row.price_date for row in rows}

    @staticmethod
    def _to_domain(row) -> DailyPrice:
        return DailyPrice(
            company_id=row.company_id,
            price_date=row.price_date,
            open_price=row.open,
            high_price=row.high,
            low_price=row.low,
            close_price=row.close,
            adjusted_close=row.adjusted_close,
            volume=row.volume,
        )

    def get_prices_between(self, company_id, start_date, end_date):
        statement = (
            select(daily_prices)
            .where(daily_prices.c.company_id == company_id)
            .where(daily_prices.c.price_date.between(start_date, end_date))
            .order_by(daily_prices.c.price_date)
        )
        with self.engine.connect() as conn:
            return [self._to_domain(row) for row in conn.execute(statement)]

    def list_by_company(self, company_id: int) -> list[DailyPrice]:
        statement = (
            select(daily_prices)
            .where(daily_prices.c.company_id == company_id)
            .order_by(daily_prices.c.price_date)
        )
        with self.engine.connect() as conn:
            return [self._to_domain(row) for row in conn.execute(statement)]

    def count(self, company_id: int | None = None) -> int:
        statement = select(func.count()).select_from(daily_prices)
        if company_id is not None:
            statement = statement.where(daily_prices.c.company_id == company_id)
        with self.engine.connect() as conn:
            return conn.execute(statement).scalar_one()
