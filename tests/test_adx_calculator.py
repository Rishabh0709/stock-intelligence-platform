from src.bootstrap import Bootstrap
from src.analytics.indicators.adx_calculator import ADXCalculator


bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = ADXCalculator(
    stock.price_series,
)

print()

print("===== Latest ADX =====")

print(calculator.latest())

print()

print("===== Last 10 ADX =====")

for row in calculator.adx()[-10:]:
    print(row)