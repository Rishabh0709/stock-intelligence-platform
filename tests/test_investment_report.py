from src.bootstrap import Bootstrap

from src.recommendation.investment_report_builder import (
    InvestmentReportBuilder,
)

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

builder = InvestmentReportBuilder()

report = builder.build(stock)

print()

print("Recommendation")
print(report.recommendation)

print()

print("Trend")
print(report.trend)

print()

print("Momentum")
print(report.momentum)

print()

print("Risk")
print(report.risk)

print()

print("Volatility")
print(report.volatility)