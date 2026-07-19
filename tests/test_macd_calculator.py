from src.bootstrap import Bootstrap
from src.analytics.indicators.macd_calculator import MACDCalculator


bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = MACDCalculator(
    stock.price_series,
)

print()

print("===== Latest MACD =====")

print(calculator.latest())

print()

print("===== Last 10 =====")

for row in calculator.macd()[-10:]:
    print(row)