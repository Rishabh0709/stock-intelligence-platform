from pathlib import Path

from src.bootstrap import Bootstrap

CSV_FILE = r"C:\Users\Advik\Downloads\holdings_statement.csv"


bootstrap = Bootstrap()

print("=" * 80)
print("INITIAL DATABASE STATE")
print("=" * 80)

print(f"Companies           : {bootstrap.company_repository.count()}")
print(f"Portfolio Holdings  : {len(bootstrap.portfolio_repository.get_all())}")
print(f"Price Records       : {bootstrap.price_repository.count()}")

print()

print("=" * 80)
print("STARTING IMPORT")
print("=" * 80)

count = bootstrap.portfolio_import_service.import_holdings(
    Path(CSV_FILE)
)

print()
print("=" * 80)
print("IMPORT FINISHED")
print("=" * 80)

print(f"Imported Holdings : {count}")

print()
print("=" * 80)
print("DATABASE STATE")
print("=" * 80)

print(f"Companies           : {bootstrap.company_repository.count()}")
print(f"Portfolio Holdings  : {len(bootstrap.portfolio_repository.get_all())}")

print()

print("=" * 80)
print("COMPANIES")
print("=" * 80)

for company in bootstrap.company_service.get_all_companies():
    print(
        company.id,
        company.symbol,
        company.isin,
    )

print()

print("=" * 80)
print("PORTFOLIO")
print("=" * 80)

for holding in bootstrap.portfolio_repository.get_all():

    company = bootstrap.company_repository.get(
        holding.company_id,
    )

    print(
        company.symbol,
        holding.quantity,
        holding.average_price,
    )

print()

print("=" * 80)
print("PRICE RECORDS")
print("=" * 80)

for company in bootstrap.company_service.get_all_companies():

    prices = bootstrap.price_repository.list_by_company(
        company.id,
    )

    print(
        f"{company.symbol:<15} {len(prices)}"
    )

print()

print("=" * 80)
print("DONE")
print("=" * 80)