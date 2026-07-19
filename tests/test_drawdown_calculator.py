from src.bootstrap import Bootstrap
from src.analytics.core.drawdown_calculator import DrawdownCalculator


bootstrap = Bootstrap()

explorer = bootstrap.stock_explorer_service

stock = explorer.get_stock("RELIANCE")

calculator = DrawdownCalculator(
    stock.price_series,
)

print()

print("===== Latest Drawdown =====")
print(calculator.latest())

print()

print("===== Maximum Drawdown =====")
print(calculator.maximum())

print()

print("===== Last 10 Drawdowns =====")

for row in calculator.historical()[-10:]:
    print(row)