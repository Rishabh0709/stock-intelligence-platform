from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    Numeric,
    Boolean,
    Text,
    String,
    Float,
    Date,
    DateTime,
    BigInteger,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.sql import func
from datetime import datetime

metadata = MetaData()

# ==========================================================
# Companies
# ==========================================================

companies = Table(
    "companies",
    metadata,

    Column("id", Integer, primary_key=True, autoincrement=True),

    Column("symbol", String(20), nullable=False, unique=True),
    Column("company_name", String(255), nullable=False),
    Column("exchange", String(20), nullable=False),

    Column("isin", String(20)),
    Column("sector", String(100)),
    Column("industry", String(100)),

    Column("country", String(50)),
    Column("currency", String(10)),

    Column("website", String(255)),
    Column("business_description", Text),

    Column(
        "created_at",
        DateTime,
        server_default=func.now(),
        nullable=False,
    ),
)

# ==========================================================
# Daily Prices
# ==========================================================

daily_prices = Table(
    "daily_prices",
    metadata,

    Column("id", Integer, primary_key=True, autoincrement=True),

    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
    ),

    Column("price_date", Date, nullable=False),

    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
    Column("adjusted_close", Float),

    Column("volume", BigInteger),

    Column(
        "created_at",
        DateTime,
        server_default=func.now(),
        nullable=False,
    ),

    UniqueConstraint(
        "company_id",
        "price_date",
        name="uq_company_price_date",
    ),
)


# ==========================================================
# Portfolio Holdings
# =========================================================

portfolio_holdings = Table(
    "portfolio_holdings",
    metadata,

    Column(
        "id",
        Integer,
        primary_key=True,
        autoincrement=True,
    ),

    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id"),
        nullable=False,
    ),

    Column(
        "quantity",
        Float,
        nullable=False,
    ),

    Column(
        "average_price",
        Float,
        nullable=False,
    ),

    Column(
        "created_at",
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    ),

    Column(
        "updated_at",
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    ),

    UniqueConstraint(
        "company_id",
        name="uq_portfolio_company",
    ),
)