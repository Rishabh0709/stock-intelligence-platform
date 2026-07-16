from bootstrap import Bootstrap

from src.analytics.core.cagr_calculator import CAGRCalculator

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")


calculator = CAGRCalculator(stock.series)

print(f"CAGR : {calculator.calculate():.2%}")