from src.bootstrap import Bootstrap

from src.analytics.indicators.moving_average_calculator import (
    MovingAverageCalculator,
)

bootstrap = Bootstrap()

explorer = bootstrap.stock_explorer_service

stock = explorer.get_stock("RELIANCE")

calculator = MovingAverageCalculator(
    stock.price_series,
)

print()
print("===== SMA 20 =====")

for row in calculator.sma(20)[-10:]:
    print(row)

print()
print("===== EMA 20 =====")

for row in calculator.ema(20)[-10:]:
    print(row)