"""Adopt the existing application schema without deleting user data."""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_existing_schema_baseline"
down_revision: str | Sequence[str] | None = None
branch_labels = None
depends_on = None


def _table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    existing = _table_names()

    if "companies" not in existing:
        op.create_table(
            "companies",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("symbol", sa.String(20), nullable=False, unique=True),
            sa.Column("company_name", sa.String(255), nullable=False),
            sa.Column("exchange", sa.String(20), nullable=False),
            sa.Column("isin", sa.String(20)),
            sa.Column("sector", sa.String(100)),
            sa.Column("industry", sa.String(100)),
            sa.Column("country", sa.String(50)),
            sa.Column("currency", sa.String(10)),
            sa.Column("website", sa.String(255)),
            sa.Column("business_description", sa.Text()),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
        )

    if "daily_prices" not in existing:
        op.create_table(
            "daily_prices",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "company_id",
                sa.Integer(),
                sa.ForeignKey("companies.id"),
                nullable=False,
            ),
            sa.Column("price_date", sa.Date(), nullable=False),
            sa.Column("open", sa.Float()),
            sa.Column("high", sa.Float()),
            sa.Column("low", sa.Float()),
            sa.Column("close", sa.Float()),
            sa.Column("adjusted_close", sa.Float()),
            sa.Column("volume", sa.BigInteger()),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint(
                "company_id",
                "price_date",
                name="uq_company_price_date",
            ),
        )

    if "portfolio_holdings" not in existing:
        op.create_table(
            "portfolio_holdings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "company_id",
                sa.Integer(),
                sa.ForeignKey("companies.id"),
                nullable=False,
            ),
            sa.Column("quantity", sa.Float(), nullable=False),
            sa.Column("average_price", sa.Float(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.UniqueConstraint("company_id", name="uq_portfolio_company"),
        )

    if "watchlist_items" not in existing:
        op.create_table(
            "watchlist_items",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "company_id",
                sa.Integer(),
                sa.ForeignKey("companies.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("entry_price", sa.Float()),
            sa.Column("target_price", sa.Float()),
            sa.Column("alert_price", sa.Float()),
            sa.Column("priority", sa.String(20), nullable=False, server_default="Medium"),
            sa.Column("status", sa.String(20), nullable=False, server_default="Watching"),
            sa.Column("thesis", sa.Text()),
            sa.Column("notes", sa.Text()),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.UniqueConstraint("company_id", name="uq_watchlist_company"),
        )


def downgrade() -> None:
    # This revision may have adopted pre-existing user tables. Dropping them
    # would be destructive, so the safe downgrade intentionally does nothing.
    pass
