"""Apply all pending database migrations.

Run from the project root:
    python scripts/migrate_database.py
"""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import DATABASE_URL
from src.database.migrations import upgrade_database


if __name__ == "__main__":
    upgrade_database(DATABASE_URL)
    print("Database is at the latest schema revision.")
