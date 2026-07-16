import pandas_ta as ta

from src.analytics.constants import DEFAULT_ADX_PERIOD
from src.analytics.indicators.indicator_base import IndicatorBase
from src.analytics.indicator_result import IndicatorResult
from src.models.adx import ADX


class ADXCalculator(IndicatorBase):
    """
    Calculates Average Directional Index (ADX).
    """

    def __init__(
        self,
        series,
        period: int = DEFAULT_ADX_PERIOD,
    ):
        super().__init__(series)
        self.period = period

    # ==========================================================
    # Series
    # ==========================================================

    def adx_series(
        self,
    ) -> list[ADX]:

        if not self.has_enough_data(self.period):

            return [
                ADX(
                    date=date,
                    plus_di=None,
                    minus_di=None,
                    adx=None,
                )
                for date in self.series.dates
            ]

        df = ta.adx(
            high=self.dataframe["High"],
            low=self.dataframe["Low"],
            close=self.dataframe["Adj Close"],
            length=self.period,
        )

        plus_di_values = self.pandas_to_list(
            df.iloc[:, 0]
        )

        minus_di_values = self.pandas_to_list(
            df.iloc[:, 1]
        )

        adx_values = self.pandas_to_list(
            df.iloc[:, 2]
        )

        history: list[ADX] = []

        for (
            date,
            plus_di,
            minus_di,
            adx,
        ) in zip(
            self.series.dates,
            plus_di_values,
            minus_di_values,
            adx_values,
        ):

            history.append(
                ADX(
                    date=date,
                    plus_di=plus_di,
                    minus_di=minus_di,
                    adx=adx,
                )
            )

        return history

    # ==========================================================
    # Signal
    # ==========================================================

    @staticmethod
    def _signal(
        adx: ADX | None,
    ) -> str | None:

        if (
            adx is None
            or adx.adx is None
            or adx.plus_di is None
            or adx.minus_di is None
        ):
            return None

        #
        # Ignore weak trends
        #
        if adx.adx < 25:
            return "HOLD"

        if adx.plus_di > adx.minus_di:
            return "BUY"

        if adx.plus_di < adx.minus_di:
            return "SELL"

        return "HOLD"

    @staticmethod
    def _interpretation(
        adx: ADX | None,
    ) -> str | None:

        if adx is None or adx.adx is None:
            return None

        if adx.adx < 20:
            return "Weak trend"

        if adx.adx < 25:
            return "Trend developing"

        if adx.adx < 40:
            return "Strong trend"

        return "Very strong trend"

    # ==========================================================
    # Public API
    # ==========================================================

    def calculate(
        self,
    ) -> IndicatorResult[ADX]:

        history = self.adx_series()

        latest = self.latest(history)

        return self.create_result(
            name=f"ADX({self.period})",
            history=history,
            signal=self._signal(latest),
            interpretation=self._interpretation(latest),
        )

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def adx(
        self,
    ) -> IndicatorResult[ADX]:

        return self.calculate()