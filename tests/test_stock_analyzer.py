from src.bootstrap import Bootstrap
from src.analysis.stock_analyzer import StockAnalyzer


bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

analysis = StockAnalyzer(stock)

print()

print("Company")

print(stock.company.company_name)

print()

print("Latest RSI")

print(analysis.rsi.latest())

print()

print("Latest MACD")

print(analysis.macd.latest())

print()

print("Latest ATR")

print(analysis.atr.latest())

print()

print("Latest ADX")

print(analysis.adx.latest())

print()

print("Latest Bollinger")

print(analysis.bollinger.latest())

print()

print("Trend")
print(analysis.trend.analyze())

print()

print("Momentum")
print(analysis.momentum.analyze())

print()

print("Risk")
print(analysis.risk.analyze())

print()

print("Volatility")
print(analysis.volatility.analyze())

print()

print("Maximum Drawdown")

print(analysis.drawdown.maximum())

print()

print("CAGR")

print(analysis.returns.cagr())