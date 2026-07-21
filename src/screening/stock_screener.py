from src.analysis.stock_analyzer import StockAnalyzer

from src.analytics.core.price_series import PriceSeries

from src.models.stock_data import StockData

from src.screening.dto.screener_result import ScreenerResult


class StockScreener:

    """
    Runs the complete analysis pipeline across all companies.
    """

    MIN_HISTORY = 200

    def __init__(
        self,
        company_repository,
        portfolio_repository,
        price_repository,
        score_engine,
        recommendation_engine,
    ):
        self.company_repository = company_repository
        self.portfolio_repository = portfolio_repository
        self.price_repository = price_repository
        self.score_engine = score_engine
        self.recommendation_engine = recommendation_engine

    def screen(
        self,
        recommendation: str = "All",
        min_score: int = 0
    ) -> list[ScreenerResult]:

        
        results = []
        
        holdings = self.portfolio_repository.get_all()

        for holding in holdings:

            company = self.company_repository.get(
                holding.company_id,
            )
        
            prices = self.price_repository.list_by_company(
                company.id,
            )

            if len(prices) < self.MIN_HISTORY:
                continue

            stock = StockData(
                company=company,
                price_series=PriceSeries(prices),
            )

            analyzer = StockAnalyzer(stock)

            score = self.score_engine.score(
                analyzer,
            )

            recommendation = self.recommendation_engine.recommend(
                score,
            )

            latest_price = stock.price_series.latest_close()

            results.append(

                ScreenerResult(

                    company=company,

                    latest_price=latest_price,

                    score=score,

                    recommendation=recommendation,
                )

            )

        return sorted(
            results,
            key=lambda x: x.score.normalized_score,
            reverse=True,
        )
    
    
    
    def get_screener_results(
        self,
        min_score: int,
        recommendation: str,
        ):
        return self.stock_screener.screen(
            min_score=min_score,
            recommendation=recommendation,
        )