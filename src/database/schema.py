from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime,
)

metadata = MetaData()

companies = Table(
    "companies",
    metadata,

    Column("id", Integer, primary_key=True),

    Column("symbol", String(20), nullable=False, unique=True),

    Column("company_name", String(255), nullable=False),

    Column("exchange", String(20), nullable=False),

    Column("isin", String(20), unique=True),

    Column("sector", String(100)),

    Column("industry", String(100)),

    Column("country", String(100)),

    Column("currency", String(20)),

    Column("website", String(255)),

    Column("business_description", String),

    Column("created_at", DateTime)
)