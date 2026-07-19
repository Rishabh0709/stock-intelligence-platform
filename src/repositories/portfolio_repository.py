from abc import ABC, abstractmethod
from sqlalchemy import select, insert, update, delete

from src.models.portfolio_holding import PortfolioHolding

from src.database.db_manager import DatabaseManager
from src.database.tables import portfolio_holdings




class IPortfolioRepository(ABC):

    @abstractmethod
    def get_all(self) -> list[PortfolioHolding]:
        ...

    @abstractmethod
    def get(
        self,
        company_id: int,
    ) -> PortfolioHolding | None:
        ...

    @abstractmethod
    def add(
        self,
        holding: PortfolioHolding,
    ) -> PortfolioHolding:
        ...

    @abstractmethod
    def update(
        self,
        holding: PortfolioHolding,
    ) -> PortfolioHolding:
        ...

    @abstractmethod
    def upsert(
        self,
        holding: PortfolioHolding,
    ) -> PortfolioHolding:
        ...

    @abstractmethod
    def delete(
        self,
        company_id: int,
    ) -> None:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...
    


class SQLitePortfolioRepository(IPortfolioRepository):

    def __init__(
        self,
        db: DatabaseManager,
    ):
        self.db = db

    def get_all(self) -> list[PortfolioHolding]:

        stmt = (
            select(portfolio_holdings)
            .order_by(portfolio_holdings.c.company_id)
        )

        with self.db.engine.connect() as conn:

            rows = conn.execute(stmt).mappings().all()

        return [
            PortfolioHolding(**row)
            for row in rows
        ]

    def get(
        self,
        company_id: int,
        ) -> PortfolioHolding | None:

        stmt = (
            select(portfolio_holdings)
            .where(
                portfolio_holdings.c.company_id == company_id
            )
        )

        with self.db.engine.connect() as conn:

            row = conn.execute(stmt).mappings().first()

        return (
            PortfolioHolding(**row)
            if row
            else None
        )

    def add(
        self,
        holding: PortfolioHolding,
        ) -> PortfolioHolding:

        values = {
            "company_id": holding.company_id,
            "quantity": holding.quantity,
            "average_price": holding.average_price,
        }

        stmt = insert(portfolio_holdings).values(**values)

        with self.db.engine.begin() as conn:

            result = conn.execute(stmt)

            holding.id = result.inserted_primary_key[0]

        return holding

    def update(
        self,
        holding: PortfolioHolding,
        ) -> PortfolioHolding:

        stmt = (
            update(portfolio_holdings)
            .where(
                portfolio_holdings.c.company_id == holding.company_id
            )
            .values(
                quantity=holding.quantity,
                average_price=holding.average_price,
            )
        )

        with self.db.engine.begin() as conn:

            conn.execute(stmt)

        return holding

    def upsert(
        self,
        holding: PortfolioHolding,
        ) -> PortfolioHolding:

        existing = self.get(
            holding.company_id,
        )

        if existing:

            return self.update(holding)

        return self.add(holding)

    def delete(
        self,
        company_id: int,
        ) -> None:

        stmt = (
            delete(portfolio_holdings)
            .where(
                portfolio_holdings.c.company_id == company_id
            )
        )

        with self.db.engine.begin() as conn:

            conn.execute(stmt)

    def clear(self) -> None:

        stmt = delete(portfolio_holdings)

        with self.db.engine.begin() as conn:

            conn.execute(stmt)

    def count(self) -> int:

        stmt = select(func.count()).select_from(portfolio_holdings)

        with self.db.engine.connect() as conn:

            return conn.execute(stmt).scalar_one()