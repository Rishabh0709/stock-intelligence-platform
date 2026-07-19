from src.bootstrap import Bootstrap
from src.analytics.indicators.atr_calculator import ATRCalculator


bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = ATRCalculator(stock.price_series)

print()
print("===== Latest ATR =====")
print(calculator.latest())

print()
print("===== Last 10 ATR =====")

for row in calculator.atr()[-10:]:
    print(row)