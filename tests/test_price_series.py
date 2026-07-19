from src.analytics.core.price_series import PriceSeries

series = PriceSeries(stock.prices)

print(series.count())

print(series.latest())

print(series.first())

print(series.close_prices[-5:])