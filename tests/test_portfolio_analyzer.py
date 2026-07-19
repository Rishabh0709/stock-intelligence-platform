from src.bootstrap import Bootstrap

bootstrap = Bootstrap()

analysis = bootstrap.portfolio_analyzer.analyze()

print(f"Investment : {analysis.total_investment}")
print(f"Current    : {analysis.current_value}")
print(f"P&L        : {analysis.total_profit_loss}")

for position in analysis.positions:

    print(
        position.symbol,
        position.profit_loss_percent,
        position.recommendation.rating,
    )