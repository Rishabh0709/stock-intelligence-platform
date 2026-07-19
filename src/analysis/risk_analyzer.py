from src.models.stock_data import StockData

from src.analysis.dto.risk_analysis import RiskAnalysis

from src.analytics.core.return_calculator import ReturnCalculator
from src.analytics.statistics.volatility_calculator import VolatilityCalculator
from src.analytics.core.drawdown_calculator import DrawdownCalculator
from src.analytics.indicators.atr_calculator import ATRCalculator


class RiskAnalyzer:

    def __init__(
        self,
        stock: StockData,
    ):

        self.stock = stock

        self.series = stock.price_series

        self.returns = ReturnCalculator(self.series)

        self.volatility = VolatilityCalculator(self.series)

        self.drawdown = DrawdownCalculator(self.series)

        self.atr = ATRCalculator(self.series)

    def analyze(self) -> RiskAnalysis:

        latest_vol = self.volatility.latest()

        latest_atr = self.atr.latest()

        cagr = self.returns.cagr()

        volatility = (
            latest_vol.volatility
            if latest_vol
            else None
        )

        current_dd = self.drawdown.latest()

        max_dd = self.drawdown.maximum()

        atr = (
            latest_atr.atr
            if latest_atr
            else None
        )

        return RiskAnalysis(

            date=self.series.latest_date(),

            cagr=cagr,

            annual_volatility=volatility,

            current_drawdown=current_dd,

            maximum_drawdown=max_dd,

            atr=atr,

            risk_level=self._risk_level(
                volatility,
                max_dd,
            ),

            drawdown_level=self._drawdown_level(
                current_dd,
            ),

            volatility_level=self._volatility_level(
                volatility,
            ),
        )

    def _volatility_level(
        self,
        volatility: float | None,
    ) -> str:

        if volatility is None:
            return "Unknown"

        if volatility < 0.20:
            return "Low"

        if volatility < 0.30:
            return "Moderate"

        if volatility < 0.40:
            return "High"

        return "Very High"

    def _drawdown_level(
        self,
        drawdown: float | None,
    ) -> str:

        if drawdown is None:
            return "Unknown"

        dd = abs(drawdown)

        if dd < 0.10:
            return "Healthy"

        if dd < 0.20:
            return "Normal"

        if dd < 0.35:
            return "Deep"

        return "Severe"

    def _risk_level(
        self,
        volatility: float | None,
        max_drawdown: float | None,
    ) -> str:

        if volatility is None or max_drawdown is None:
            return "Unknown"

        score = 0

        if volatility > 0.30:
            score += 1

        if volatility > 0.40:
            score += 1

        if abs(max_drawdown) > 0.30:
            score += 1

        if abs(max_drawdown) > 0.50:
            score += 1

        if score <= 1:
            return "Low"

        if score == 2:
            return "Medium"

        return "High"