import pandas_ta as ta

from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)
from src.models.atr import ATR


class ATRCalculator(BaseIndicatorCalculator):
    """
    Calculates True Range and Average True Range.
    """

    def atr(
        self,
        period: int = 14,
    ) -> list[ATR]:

        df = self.dataframe

        tr = ta.true_range(
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
        )

        atr = ta.atr(
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            length=period,
        )

        result = []

        for dt, tr_value, atr_value in zip(
            df["Date"],
            tr,
            atr,
        ):
            result.append(
                ATR(
                    date=self.normalize_date(dt),
                    true_range=self.to_float(tr_value),
                    atr=self.to_float(atr_value),
                )
            )

        return result

    def latest(
        self,
        period: int = 14,
    ) -> ATR | None:

        history = self.atr(period)

        if not history:
            return None

        return history[-1]