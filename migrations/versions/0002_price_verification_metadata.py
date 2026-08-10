"""Add candle provenance and verification timestamps."""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_price_verification_metadata"
down_revision: str | Sequence[str] | None = "0001_existing_schema_baseline"
branch_labels = None
depends_on = None


def _daily_price_columns() -> set[str]:
    inspector = sa.inspect(op.get_bind())
    if "daily_prices" not in inspector.get_table_names():
        return set()
    return {column["name"] for column in inspector.get_columns("daily_prices")}


def upgrade() -> None:
    columns = _daily_price_columns()
    with op.batch_alter_table("daily_prices") as batch:
        if "provider" not in columns:
            batch.add_column(sa.Column("provider", sa.String(100)))
        if "downloaded_at" not in columns:
            batch.add_column(sa.Column("downloaded_at", sa.DateTime(timezone=True)))
        if "last_verified_at" not in columns:
            batch.add_column(sa.Column("last_verified_at", sa.DateTime(timezone=True)))


def downgrade() -> None:
    columns = _daily_price_columns()
    with op.batch_alter_table("daily_prices") as batch:
        for name in ("last_verified_at", "downloaded_at", "provider"):
            if name in columns:
                batch.drop_column(name)
