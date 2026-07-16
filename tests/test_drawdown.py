from bootstrap import Bootstrap

from src.analytics.core.drawdown_calculator import DrawdownCalculator

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

calculator = DrawdownCalculator(stock.series)

print(
    f"Current Drawdown : "
    f"{calculator.current_drawdown():.2%}"
)

print(
    f"Maximum Drawdown : "
    f"{calculator.maximum_drawdown():.2%}"
)