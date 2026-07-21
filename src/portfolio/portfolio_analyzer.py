from src.analysis.stock_analyzer import StockAnalyzer

from src.portfolio.dto.portfolio_analysis import PortfolioAnalysis
from src.portfolio.dto.portfolio_position import PortfolioPosition

from src.repositories.company_repository import (
    ICompanyRepository,
)
from src.repositories.portfolio_repository import (
    IPortfolioRepository,
)
from src.repositories.price_repository import IPriceRepository

from src.models.stock_data import StockData
from src.recommendation.recommendation_engine import RecommendationEngine
from src.scoring.score_engine import ScoreEngine
from src.analytics.core.price_series import PriceSeries

class PortfolioAnalyzer:
    """
    Analyzes the complete investment portfolio.
    """

    def __init__(
        self,
        portfolio_repository: IPortfolioRepository,
        company_repository: ICompanyRepository,
        price_repository: IPriceRepository,
        recommendation_engine: RecommendationEngine,
        score_engine: ScoreEngine
    ):
        self.portfolio_repository = portfolio_repository
        self.company_repository = company_repository
        self.price_repository = price_repository
        self.recommendation_engine = recommendation_engine
        self.score_engine = score_engine

    def analyze(self) -> PortfolioAnalysis:

        positions = []

        total_investment = 0.0
        current_value = 0.0

        winners = 0
        losers = 0

        holdings = self.portfolio_repository.get_all()

        for holding in holdings:
           
            
            company = self.company_repository.get(
                holding.company_id,
            )

            print(
            company.symbol,
            company.id,
            len(self.price_repository.list_by_company(company.id))
            )    
            
            if company is None:
                continue

            prices = self.price_repository.list_by_company(
                company.id,
            )

            if not prices:
                continue

            price_series = PriceSeries(prices)
            
            stock = StockData(
                company=company,
                price_series=price_series)

            print(company.symbol, len(prices))
            analysis = StockAnalyzer(stock)
            score = self.score_engine.score(analysis)
            recommendation = self.recommendation_engine.recommend(score)
            

            latest_price = price_series.latest_close()

            invested = (
                holding.quantity *
                holding.average_price
            )

            current = (
                holding.quantity *
                latest_price
            )

            pnl = current - invested

            pnl_percent = (
                (pnl / invested) * 100
                if invested > 0
                else 0.0
            )

            if pnl >= 0:
                winners += 1
            else:
                losers += 1

            total_investment += invested
            current_value += current

            positions.append(
                PortfolioPosition(
                    symbol=company.symbol,
                    quantity=holding.quantity,
                    average_price=holding.average_price,
                    current_price=latest_price,
                    invested_value=invested,
                    current_value=current,
                    profit_loss=pnl,
                    profit_loss_percent=pnl_percent,
                    recommendation=recommendation,
                )
            )

        total_profit = current_value - total_investment

        total_profit_percent = (
            (total_profit / total_investment) * 100
            if total_investment > 0
            else 0.0
        )

        positions.sort(
            key=lambda x: x.current_value,
            reverse=True,
        )

        return PortfolioAnalysis(
            positions=positions,
            total_investment=total_investment,
            current_value=current_value,
            total_profit_loss=total_profit,
            total_profit_loss_percent=total_profit_percent,
            winners=winners,
            losers=losers,
        )