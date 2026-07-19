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
    
        #print(f'latest ema: {self.ema(period)[-1]}')
        return self.ema(period)[-1]
    
    def latest_sma(self, period: int = 20):
        
        #print(f'latest sma: {self.sma(period)[-1]}')
        return self.sma(period)[-1]