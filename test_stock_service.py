from sqlalchemy import text

with bootstrap.price_repository.engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            open,
            high,
            low,
            close,
            adjusted_close
        FROM daily_prices
        LIMIT 5
    """))

    for row in result:
        print(row)