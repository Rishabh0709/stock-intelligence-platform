from bootstrap import Bootstrap

from src.analytics.indicators.moving_average_calculator import (
    MovingAverageCalculator,
)

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock(
    "RELIANCE"
)

ma = MovingAverageCalculator(
    stock.series
)

print()

print("20 SMA :", ma.sma(20))

print("50 SMA :", ma.sma(50))

print("200 SMA:", ma.sma(200))

print()

print("20 EMA :", ma.ema(20))

print("50 EMA :", ma.ema(50))

print("200 EMA:", ma.ema(200))