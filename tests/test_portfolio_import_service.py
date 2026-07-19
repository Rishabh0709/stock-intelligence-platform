from src.bootstrap import Bootstrap

bootstrap = Bootstrap()

count = bootstrap.portfolio_import_service.import_holdings(
    file_path = 'C:\\Users\\Advik\\Downloads\\holdings_statement.csv'
)

print()

company = bootstrap.company_repository.get_by_symbol("TCS")
print(company)

company = bootstrap.company_repository.get_by_symbol("SBIN")
print(company)

company = bootstrap.company_repository.get_by_symbol("RELIANCE")
print(company)

#print(f"Imported {count} holdings")

print()

#for holding in bootstrap.portfolio_repository.get_all():
    #print(holding)