from config.settings import DATABASE_PATH

from src.database.db_manager import DatabaseManager
from src.models.company import Company
from src.repositories.company_repository import (
    SQLiteCompanyRepository,
)
from src.services.company_service import CompanyService


def main():

    print("=" * 60)
    print("Stock Intelligence Platform")
    print("=" * 60)

    db = DatabaseManager()

    success, error = db.test_connection()

    if not success:
        print(error)
        return

    print("✓ Database connected")

    db.create_tables()

    print("✓ Tables created")

    repository = SQLiteCompanyRepository(db)

    service = CompanyService(repository)

    company = Company(
        symbol="RELIANCE",
        company_name="Reliance Industries Ltd",
        exchange="NSE",
        country="India",
        currency="INR",
    )

    try:
        service.register_company(company)
        print("✓ Company saved")

    except ValueError as e:
        print(e)

    saved_company = service.get_company("RELIANCE")

    print("\nRetrieved Company\n")
    print(saved_company)

    print("\nDatabase Path:")
    print(DATABASE_PATH)

    print("=" * 60)
    print("System Ready")
    print("=" * 60)


if __name__ == "__main__":
    main()