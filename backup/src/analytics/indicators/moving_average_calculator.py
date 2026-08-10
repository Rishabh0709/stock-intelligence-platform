from datetime import date

import pandas as pd
import pandas_ta as ta

from src.analytics.core.price_series import PriceSeries
from src.models.moving_average import MovingAverage


class MovingAverageCalculator:

    def __init__(self, series: PriceSeries):
        self.series = series

    def _build(
    self,
    dates,
    values,
    *,
    is_sma: bool,
    ) -> list[MovingAverage]:

        if values is None:
            return []

        result = []

        for dt, value in zip(dates, values):

            if isinstance(dt, pd.Timestamp):
                dt = dt.date()

            value = (
            None
            if pd.isna(value)
            else float(value)
            )

            result.append(
                MovingAverage(
                date=dt,
                sma=value if is_sma else None,
                ema=None if is_sma else value,
                )
            )

        return result

    def sma(
        self,
        period: int = 20,
    ) -> list[MovingAverage]:

        df = self.series.dataframe.copy()

        if len(df) < period:
            return []
        
        values = ta.sma(
            df["Close"],
            length=period,
        )

        return self._build(
            df["Date"],
            values,
            is_sma=True,
        )

    def ema(
        self,
        period: int = 20,
    ) -> list[MovingAverage]:

        df = self.series.dataframe.copy()

        if len(df) < period:
            return []
        
        values = ta.ema(
            df["Close"],
            length=period,
        )

        return self._build(
            df["Date"],
            values,
            is_sma=False,
        )
        
    def latest_ema(self, period: int = 20):

        averages = self.ema(period)

        if not averages:
            return MovingAverage(
            date=self.series.latest_date(),
            sma=None,
            ema=None,
            )

        return averages[-1]
    
    
    def latest_sma(self, period: int = 20):

        averages = self.sma(period)

        if not averages:
            return MovingAverage(
            date=self.series.latest_date(),
            sma=None,
            ema=None,
            )

        return averages[-1]