from bootstrap import Bootstrap

from src.analytics.core.volatility_calculator import VolatilityCalculator


bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")


calculator = VolatilityCalculator(stock.series)

volatility = calculator.calculate()

print(f"Volatility : {volatility:.2%}")