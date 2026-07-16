from sqlalchemy import select
from src.database.tables import daily_prices

stmt = (
    select(daily_prices)
    .where(daily_prices.c.company_id == company.id)
    .order_by(daily_prices.c.price_date.desc())
    .limit(5)
)

with bootstrap.price_repository.engine.connect() as conn:
    for row in conn.execute(stmt):
        print(row)