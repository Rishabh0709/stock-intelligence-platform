from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import delete, insert, select, update

from src.database.tables import companies, watchlist_items
from src.models.watchlist_item import WatchlistItem


class IWatchlistRepository(ABC):

    @abstractmethod
    def upsert(self, item: WatchlistItem) -> WatchlistItem:
        pass

    @abstractmethod
    def get_by_company(self, company_id: int) -> WatchlistItem | None:
        pass

    @abstractmethod
    def list_all(self) -> list[WatchlistItem]:
        pass

    @abstractmethod
    def delete(self, company_id: int) -> None:
        pass


class SQLiteWatchlistRepository(IWatchlistRepository):

    def __init__(self, db_manager):
        self.db_manager = db_manager

    @property
    def engine(self):
        return self.db_manager.engine

    @staticmethod
    def _to_domain(row) -> WatchlistItem:
        return WatchlistItem(
            id=row.id,
            company_id=row.company_id,
            symbol=row.symbol,
            company_name=row.company_name,
            entry_price=row.entry_price,
            target_price=row.target_price,
            alert_price=row.alert_price,
            priority=row.priority,
            status=row.status,
            thesis=row.thesis,
            notes=row.notes,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def upsert(self, item: WatchlistItem) -> WatchlistItem:
        existing = self.get_by_company(item.company_id)
        now = datetime.now(UTC)
        values = {
            "target_price": item.target_price,
            "alert_price": item.alert_price,
            "updated_at": now,
        }

        with self.engine.begin() as conn:
            if existing is None:
                conn.execute(
                    insert(watchlist_items).values(
                        company_id=item.company_id,
                        created_at=now,
                        **values,
                    )
                )
            else:
                conn.execute(
                    update(watchlist_items)
                    .where(watchlist_items.c.company_id == item.company_id)
                    .values(**values)
                )

        saved = self.get_by_company(item.company_id)
        if saved is None:
            raise RuntimeError("Watchlist item was not saved")
        return saved

    def get_by_company(self, company_id: int) -> WatchlistItem | None:
        stmt = (
            select(
                watchlist_items,
                companies.c.symbol,
                companies.c.company_name,
            )
            .join(companies, companies.c.id == watchlist_items.c.company_id)
            .where(watchlist_items.c.company_id == company_id)
        )

        with self.engine.connect() as conn:
            row = conn.execute(stmt).mappings().first()

        return None if row is None else self._to_domain(row)

    def list_all(self) -> list[WatchlistItem]:
        stmt = (
            select(
                watchlist_items,
                companies.c.symbol,
                companies.c.company_name,
            )
            .join(companies, companies.c.id == watchlist_items.c.company_id)
            .order_by(
                watchlist_items.c.priority,
                companies.c.symbol,
            )
        )

        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().all()

        return [self._to_domain(row) for row in rows]

    def delete(self, company_id: int) -> None:
        stmt = delete(watchlist_items).where(
            watchlist_items.c.company_id == company_id
        )
        with self.engine.begin() as conn:
            conn.execute(stmt)
