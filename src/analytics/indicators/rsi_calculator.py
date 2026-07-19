from src.analytics.core.price_series import PriceSeries
from src.models.rsi import RSI

import pandas as pd
import pandas_ta as ta


from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)


class RSICalculator(BaseIndicatorCalculator):

    def __init__(
        self,
        series: PriceSeries,
    ):
        super().__init__(series)

    def rsi(
        self,
        period: int = 14,
    ) -> list[RSI]:

        df = self.series.dataframe.copy()

        values = ta.rsi(
            df["Close"],
            length=period,
        )

        return [
            RSI(
                date=self.normalize_date(dt),
                rsi=self.to_float(value),
            )
            for dt, value in zip(df["Date"], values)
        ]

    def latest(
        self,
        period: int = 14,
    ) -> float | None:

        history = self.rsi(period)

        if not history:
            return None

        return history[-1].rsi