from src.models.stock_data import StockData

from src.analytics.core.return_calculator import ReturnCalculator
from src.analytics.statistics.volatility_calculator import VolatilityCalculator
from src.analytics.core.drawdown_calculator import DrawdownCalculator

from src.analytics.indicators.moving_average_calculator import (
    MovingAverageCalculator,
)
from src.analytics.indicators.rsi_calculator import RSICalculator
from src.analytics.indicators.macd_calculator import MACDCalculator
from src.analytics.indicators.atr_calculator import ATRCalculator
from src.analytics.indicators.adx_calculator import ADXCalculator
from src.analytics.indicators.bollinger_band_calculator import (
    BollingerBandCalculator,
)

from src.analysis.trend_analyzer import TrendAnalyzer
from src.analysis.momentum_analyzer import MomentumAnalyzer
from src.analysis.volatility_analyzer import VolatilityAnalyzer
from src.analysis.risk_analyzer import RiskAnalyzer

class StockAnalyzer:

    """
    High-level analysis API for a single stock.

    Acts as the entry point for all analytics.
    """

    def __init__(
        self,
        stock: StockData,
    ):
        series = stock.price_series
        
        # Analyzers
        self.trend = TrendAnalyzer(stock)
        self.momentum = MomentumAnalyzer(stock)
        self.volatility = VolatilityAnalyzer(stock)
        self.risk = RiskAnalyzer(stock)
        
        self.stock = stock
        
        # Calculators
        self.returns = ReturnCalculator(series)
        self.volatility_calculator = VolatilityCalculator(series)
        self.drawdown = DrawdownCalculator(series)

        self.moving_average = MovingAverageCalculator(series)
        self.rsi = RSICalculator(series)
        self.macd = MACDCalculator(series)
        self.atr = ATRCalculator(series)
        self.adx = ADXCalculator(series)
        self.bollinger = BollingerBandCalculator(series)