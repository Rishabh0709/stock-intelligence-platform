import pandas_ta as ta

from src.analytics.constants import (
    DEFAULT_MACD_FAST,
    DEFAULT_MACD_SIGNAL,
    DEFAULT_MACD_SLOW,
)
from src.analytics.indicators.indicator_base import IndicatorBase
from src.analytics.indicator_result import IndicatorResult
from src.models.macd import MACD


class MACDCalculator(IndicatorBase):
    """
    Calculates MACD (Moving Average Convergence Divergence).
    """

    def __init__(
        self,
        series,
        fast: int = DEFAULT_MACD_FAST,
        slow: int = DEFAULT_MACD_SLOW,
        signal: int = DEFAULT_MACD_SIGNAL,
    ):
        super().__init__(series)

        self.fast = fast
        self.slow = slow
        self.signal = signal

    # ==========================================================
    # Series
    # ==========================================================

    def macd_series(
        self,
    ) -> list[MACD]:

        df = ta.macd(
            close=self.dataframe["Adj Close"],
            fast=self.fast,
            slow=self.slow,
            signal=self.signal,
        )

        if df is None:
            return [
                MACD(
                    date=date,
                    macd=None,
                    signal=None,
                    histogram=None,
                )
                for date in self.series.dates
            ]

        macd_values = self.pandas_to_list(df.iloc[:, 0])
        signal_values = self.pandas_to_list(df.iloc[:, 1])
        histogram_values = self.pandas_to_list(df.iloc[:, 2])

        history: list[MACD] = []

        for date, macd, signal, histogram in zip(
            self.series.dates,
            macd_values,
            signal_values,
            histogram_values,
        ):
            history.append(
                MACD(
                    date=date,
                    macd=macd,
                    signal=signal,
                    histogram=histogram,
                )
            )

        return history

    # ==========================================================
    # Signal
    # ==========================================================

    @staticmethod
    def _signal(
        macd: MACD | None,
    ) -> str | None:

        if (
            macd is None
            or macd.macd is None
            or macd.signal is None
        ):
            return None

        if macd.macd > macd.signal:
            return "BUY"

        if macd.macd < macd.signal:
            return "SELL"

        return "HOLD"

    @staticmethod
    def _interpretation(
        macd: MACD | None,
    ) -> str | None:

        if (
            macd is None
            or macd.macd is None
            or macd.signal is None
        ):
            return None

        if macd.macd > macd.signal:
            return "Bullish crossover"

        if macd.macd < macd.signal:
            return "Bearish crossover"

        return "Neutral"

    # ==========================================================
    # Public API
    # ==========================================================

    def calculate(
        self,
    ) -> IndicatorResult[MACD]:

        history = self.macd_series()

        latest = self.latest(history)

        return self.create_result(
            name=(
                f"MACD("
                f"{self.fast},"
                f"{self.slow},"
                f"{self.signal})"
            ),
            history=history,
            signal=self._signal(latest),
            interpretation=self._interpretation(latest),
        )

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def macd(
        self,
    ) -> IndicatorResult[MACD]:

        return self.calculate()