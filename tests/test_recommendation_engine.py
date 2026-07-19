from src.bootstrap import Bootstrap
from src.analysis.stock_analyzer import StockAnalyzer

from src.scoring.score_engine import ScoreEngine
from src.scoring.rules.trend_rule import TrendRule
from src.scoring.rules.momentum_rule import MomentumRule
from src.scoring.rules.risk_rule import RiskRule
from src.scoring.rules.volatility_rule import VolatilityRule

from src.recommendation.recommendation_engine import RecommendationEngine

bootstrap = Bootstrap()

stock = bootstrap.stock_explorer_service.get_stock("RELIANCE")

analysis = StockAnalyzer(stock)

engine = ScoreEngine(
    rules=[
        TrendRule(),
        MomentumRule(),
        RiskRule(),
        VolatilityRule(),
    ]
)

score = engine.score(analysis)

recommendation = RecommendationEngine().recommend(score)

print(recommendation)