from src.bootstrap import Bootstrap
from src.analytics.indicators.rsi_calculator import RSICalculator

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = RSICalculator(stock.price_series)

result = calculator.rsi()

print()
from src.bootstrap import Bootstrap
from src.analytics.indicators.rsi_calculator import RSICalculator


bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = RSICalculator(
    stock.price_series,
)

print()

print("===== Latest RSI =====")
print(calculator.latest())

print()

print("===== Last 10 RSI =====")

for row in calculator.rsi()[-10:]:
    print(row)