from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_PATH = BASE_DIR / "database" / "stock_data.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
APP_NAME = "Stock Intelligence Platform"
APP_VERSION = "0.1.0"