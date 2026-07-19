from src.bootstrap import Bootstrap
from src.analysis.stock_analyzer import StockAnalyzer

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

analysis = StockAnalyzer(stock)

print()
print(analysis.momentum.analyze())