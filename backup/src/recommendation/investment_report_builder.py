from src.analysis.stock_analyzer import StockAnalyzer
from src.models.stock_data import StockData

from src.recommendation.dto.investment_report import InvestmentReport
from src.recommendation.recommendation_engine import RecommendationEngine

from src.scoring.score_engine import ScoreEngine


class InvestmentReportBuilder:
    """
    Builds the complete investment report for a stock.
    """

    def __init__(self):

        self.score_engine = ScoreEngine()

        self.recommendation_engine = RecommendationEngine()

    def build(
        self,
        stock: StockData,
    ) -> InvestmentReport:

        analysis = StockAnalyzer(stock)

        trend = analysis.trend.analyze()

        momentum = analysis.momentum.analyze()

        risk = analysis.risk.analyze()

        volatility = analysis.volatility.analyze()

        score = self.score_engine.score(analysis)

        recommendation = self.recommendation_engine.recommend(score)

        return InvestmentReport(
            recommendation=recommendation,
            trend=trend,
            momentum=momentum,
            risk=risk,
            volatility=volatility,
        )