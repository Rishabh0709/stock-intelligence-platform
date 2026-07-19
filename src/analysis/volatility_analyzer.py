from src.models.stock_data import StockData

from src.analysis.dto.volatility_analysis import VolatilityAnalysis

from src.analytics.statistics.volatility_calculator import VolatilityCalculator
from src.analytics.indicators.atr_calculator import ATRCalculator
from src.analytics.indicators.bollinger_band_calculator import (
    BollingerBandCalculator,
)


class VolatilityAnalyzer:

    def __init__(
        self,
        stock: StockData,
        ):
        self.stock = stock

        self.series = stock.price_series

        self.volatility = VolatilityCalculator(self.series)

        self.atr = ATRCalculator(self.series)

        self.bb = BollingerBandCalculator(self.series)

    def analyze(self) -> VolatilityAnalysis:

        latest_price = self.series.latest_close()

        latest_vol = self.volatility.latest()

        latest_atr = self.atr.latest()

        latest_bb = self.bb.latest()

        volatility = (
            latest_vol.volatility
            if latest_vol
            else None
        )

        atr = (
            latest_atr.atr
            if latest_atr
            else None
        )

        upper = (
            latest_bb.upper
            if latest_bb
            else None
        )

        middle = (
            latest_bb.middle
            if latest_bb
            else None
        )

        lower = (
            latest_bb.lower
            if latest_bb
            else None
        )

        return VolatilityAnalysis(

            date=self.series.latest_date(),

            volatility=volatility,

            atr=atr,

            upper_band=upper,

            middle_band=middle,

            lower_band=lower,

            volatility_level=self._classify(volatility),

            near_upper_band=(
                latest_price is not None
                and upper is not None
                and latest_price >= upper * 0.99
            ),

            near_lower_band=(
                latest_price is not None
                and lower is not None
                and latest_price <= lower * 1.01
            ),
        )

    def _classify(
        self,
        volatility,
    ) -> str:

        if volatility is None:
            return "Unknown"

        if volatility >= 0.40:
            return "Very High"

        if volatility >= 0.30:
            return "High"

        if volatility >= 0.20:
            return "Moderate"

        return "Low"