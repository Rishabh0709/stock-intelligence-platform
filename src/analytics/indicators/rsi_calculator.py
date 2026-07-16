import pandas_ta as ta

from src.analytics.constants import DEFAULT_RSI_PERIOD
from src.analytics.indicators.indicator_base import IndicatorBase
from src.analytics.indicator_result import IndicatorResult
from src.models.rsi import RSI


class RSICalculator(IndicatorBase):
    """
    Calculates Relative Strength Index (RSI).
    """

    def __init__(
        self,
        series,
        period: int = DEFAULT_RSI_PERIOD,
    ):
        super().__init__(series)
        self.period = period

    # ==========================================================
    # Series
    # ==========================================================

    def rsi_series(
        self,
    ) -> list[RSI]:

        values = ta.rsi(
            self.dataframe["Adj Close"],
            length=self.period,
        )

        numeric_values = self.pandas_to_list(
            values,
        )

        history: list[RSI | None] = []

        for date, value in zip(
            self.series.dates,
            numeric_values,
        ):

            
            history.append(
                    RSI(
                        date=date,
                        rsi=value,
                    )
                )

        return history

    # ==========================================================
    # Signal
    # ==========================================================

    @staticmethod
    def _signal(
        rsi: RSI | None,
    ) -> str | None:

        if rsi is None:
            return None

        if rsi.rsi >= 70:
            return "SELL"

        if rsi.rsi <= 30:
            return "BUY"

        return "HOLD"

    @staticmethod
    def _interpretation(
        rsi: RSI | None,
    ) -> str | None:

        if rsi is None:
            return None

        if rsi.rsi >= 70:
            return "Overbought"

        if rsi.rsi <= 30:
            return "Oversold"

        return "Neutral"

    # ==========================================================
    # Public API
    # ==========================================================

    def calculate(
        self,
    ) -> IndicatorResult[RSI]:

        history = self.rsi_series()

        latest = self.latest(
            history,
        )

        return self.create_result(
            name=f"RSI({self.period})",
            history=history,
            signal=self._signal(latest),
            interpretation=self._interpretation(latest),
        )

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def rsi(
        self,
    ) -> IndicatorResult[RSI]:

        return self.calculate()