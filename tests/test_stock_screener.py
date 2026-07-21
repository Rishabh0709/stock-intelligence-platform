from src.bootstrap import Bootstrap

bootstrap = Bootstrap()

results = bootstrap.stock_screener.screen()




print(f"Stocks Screened : {len(results)}")

print()

for result in results[:20]:

    print(
        result.company.symbol,
        result.score.score,
        result.score.normalized_score,
        result.recommendation.rating,
    )