from src.bootstrap import Bootstrap
from src.analytics.indicators.bollinger_band_calculator import (
    BollingerBandCalculator,
)

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = BollingerBandCalculator(
    stock.price_series,
)

print()

print("===== Latest Bollinger Bands =====")

print(calculator.latest())

print()

print("===== Last 10 =====")

for row in calculator.bands()[-10:]:
    print(row)