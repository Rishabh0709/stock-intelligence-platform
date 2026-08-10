from src.analysis.dto.trend_analysis import TrendAnalysis
from src.models.stock_data import StockData

from src.analytics.indicators.moving_average_calculator import (
    MovingAverageCalculator,
)
from src.analytics.indicators.adx_calculator import ADXCalculator

from src.common.enums.trend import (
    Trend,
    TrendStrength,
)


class TrendAnalyzer:
    """
    Performs trend analysis for a stock.
    """

    def __init__(
        self,
        stock: StockData,
    ):
        self.stock = stock

        self.series = stock.price_series

        self.ma = MovingAverageCalculator(self.series)

        self.adx = ADXCalculator(self.series)

    def _classify_trend(
        self,
        price: float | None,
        sma20: float | None,
        sma50: float | None,
        sma200: float | None,
    ) -> Trend:

        if None in (price, sma20, sma50, sma200):
            return Trend.NEUTRAL

        if price > sma20 > sma50 > sma200:
            return Trend.BULLISH

        if price < sma20 < sma50 < sma200:
            return Trend.BEARISH

        return Trend.NEUTRAL

    def _classify_strength(
        self,
        adx: float | None,
    ) -> TrendStrength:

        if adx is None:
            return TrendStrength.UNKNOWN

        if adx >= 30:
            return TrendStrength.STRONG

        if adx >= 20:
            return TrendStrength.MODERATE

        return TrendStrength.WEAK

    def analyze(self) -> TrendAnalysis:

        latest_price = self.series.latest_close()

        latest_date = self.series.latest_date()

        sma20 = self.ma.latest_sma(20).sma

        sma50 = self.ma.latest_sma(50).sma

        sma200 = self.ma.latest_sma(200).sma

        ema20 = self.ma.latest_ema(20).ema

        latest_adx = self.adx.latest()

        adx_value = (
            latest_adx.adx
            if latest_adx
            else None
        )

        trend = self._classify_trend(
            latest_price,
            sma20,
            sma50,
            sma200,
        )

        strength = self._classify_strength(
            adx_value,
        )

        return TrendAnalysis(
            date=latest_date,

            trend=trend,

            strength=strength,

            price=latest_price,

            sma20=sma20,

            sma50=sma50,

            sma200=sma200,

            ema20=ema20,

            adx=adx_value,

            price_above_sma20=(
                latest_price > sma20
                if latest_price is not None and sma20 is not None
                else False
            ),

            price_above_sma50=(
                latest_price > sma50
                if latest_price is not None and sma50 is not None
                else False
            ),

            sma20_above_sma50=(
                sma20 > sma50
                if sma20 is not None and sma50 is not None
                else False
            ),

            sma50_above_sma200=(
                sma50 > sma200
                if sma50 is not None and sma200 is not None
                else False
            ),
        )