from src.bootstrap import Bootstrap

from src.analytics.statistics.volatility_calculator import (
    VolatilityCalculator,
)

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = VolatilityCalculator(stock.price_series)

print()

print("Latest Volatility")
print(calculator.latest())

print()

print("Last 10")

for row in calculator.history()[-10:]:
    print(row)