from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    DateTime
)
from datetime import datetime

metadata = MetaData()

companies = Table(
    "companies",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("symbol", String, unique=True, nullable=False),
    Column("company_name", String, nullable=False),
    Column("exchange", String),
    Column("sector", String),
    Column("industry", String),
    Column("created_at", DateTime, default=datetime.utcnow),
)