import pandas_ta as ta

from src.analytics.constants import DEFAULT_ATR_PERIOD
from src.analytics.indicators.indicator_base import IndicatorBase
from src.analytics.indicator_result import IndicatorResult
from src.models.atr import ATR


class ATRCalculator(IndicatorBase):
    """
    Calculates Average True Range (ATR).
    """

    def __init__(
        self,
        series,
        period: int = DEFAULT_ATR_PERIOD,
    ):
        super().__init__(series)
        self.period = period

    # ==========================================================
    # Series
    # ==========================================================

    def atr_series(
        self,
    ) -> list[ATR]:

        tr = ta.true_range(
            high=self.dataframe["High"],
            low=self.dataframe["Low"],
            close=self.dataframe["Adj Close"],
        )

        atr = ta.atr(
            high=self.dataframe["High"],
            low=self.dataframe["Low"],
            close=self.dataframe["Adj Close"],
            length=self.period,
        )

        tr_values = self.pandas_to_list(
            tr.squeeze()
        )

        atr_values = self.pandas_to_list(
            atr.squeeze()
        )

        history: list[ATR] = []

        for date, true_range, atr_value in zip(
            self.series.dates,
            tr_values,
            atr_values,
        ):
            history.append(
                ATR(
                    date=date,
                    true_range=true_range,
                    atr=atr_value,
                )
            )

        return history

    # ==========================================================
    # Signal
    # ==========================================================

    @staticmethod
    def _signal(
        atr: ATR | None,
    ) -> str | None:

        return None

    @staticmethod
    def _interpretation(
        atr: ATR | None,
    ) -> str | None:

        if atr is None or atr.atr is None:
            return None

        return "Volatility"

    # ==========================================================
    # Public API
    # ==========================================================

    def calculate(
        self,
    ) -> IndicatorResult[ATR]:

        history = self.atr_series()

        latest = self.latest(
            history,
        )

        return self.create_result(
            name=f"ATR({self.period})",
            history=history,
            signal=self._signal(latest),
            interpretation=self._interpretation(latest),
        )

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def atr(
        self,
    ) -> IndicatorResult[ATR]:

        return self.calculate()