from src.bootstrap import Bootstrap


from src.analytics.core.return_calculator import ReturnCalculator


bootstrap = Bootstrap()

explorer = bootstrap.stock_explorer_service

stock = explorer.get_stock("RELIANCE")
company = bootstrap.company_repository.get_by_symbol("RELIANCE")
print(stock.price_series.latest())

print(company)

rows = bootstrap.price_repository.list_by_company(company.id)

print("Row count:", len(rows))
print()

for price in rows[-5:]:
    print (price)
#print(stock.price_series.close_prices[-5:])

calculator = ReturnCalculator(stock.price_series)

print()

print("Daily Return :", calculator.daily_return())

print("Total Return :", calculator.total_return())

print("CAGR :", calculator.cagr())