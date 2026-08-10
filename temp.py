from src.screening import analyze_stock, scan_stocks

report = analyze_stock(
    indicator_df,
    symbol="RELIANCE",
    account_capital=500_000,
    risk_percent=1,
)

print(report.score.score)
print(report.score.category)
print(report.active_signals)
print(report.risk)