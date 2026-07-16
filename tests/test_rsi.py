from bootstrap import Bootstrap
from src.analytics.indicators.rsi_calculator import RSICalculator

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = RSICalculator(stock.series)

result = calculator.rsi()

print()

print(result.name)

print("Current RSI :", result.value)

print("Signal      :", result.signal)

print("Meaning     :", result.interpretation)

print()

print("Last 10 RSI values")

for value in result.series[-10:]:
    print(value)