from sqlalchemy import text
from src.database.db_manager import DatabaseManager

db = DatabaseManager()

with db.engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT company_id, COUNT(*)
        FROM daily_prices
        WHERE company_id IN (1,2,3,4,5)
        GROUP BY company_id
        ORDER BY company_id
    """)).fetchall()

print(rows)