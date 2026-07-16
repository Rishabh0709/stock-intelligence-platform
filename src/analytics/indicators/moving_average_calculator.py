import pandas as pd
import pandas_ta as ta

from src.analytics.indicators.indicator_base import IndicatorBase


class MovingAverageCalculator(IndicatorBase):
    """
    Calculates Simple and Exponential Moving Averages.
    """

    # ==========================================================
    # Simple Moving Average
    # ==========================================================

    def sma_series(
        self,
        window: int,
    ) -> list[float | None]:

        if window <= 0:
            raise ValueError(
                "Window must be positive."
            )

        values = ta.sma(
            self.dataframe["Adj Close"],
            length=window,
        )

        return self.pandas_to_list(values)

    def calculate_sma(
        self,
        window: int,
    ) -> float | None:

        return self.latest(
            self.sma_series(window)
        )

    # ==========================================================
    # Exponential Moving Average
    # ==========================================================

    def ema_series(
        self,
        window: int,
    ) -> list[float | None]:

        if window <= 0:
            raise ValueError(
                "Window must be positive."
            )

        values = ta.ema(
            self.dataframe["Adj Close"],
            length=window,
        )

        return self.pandas_to_list(values)

    def calculate_ema(
        self,
        window: int,
    ) -> float | None:

        return self.latest(
            self.ema_series(window)
        )

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def sma(
        self,
        window: int,
    ) -> float | None:

        return self.calculate_sma(window)

    def ema(
        self,
        window: int,
    ) -> float | None:

        return self.calculate_ema(window)