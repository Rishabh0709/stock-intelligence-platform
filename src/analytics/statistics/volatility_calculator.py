import math

import pandas as pd

from src.analytics.core.price_series import PriceSeries
from src.models.volatility import Volatility


class VolatilityCalculator:
    """
    Calculates rolling historical volatility.

    By default returns annualized volatility using
    252 trading days.
    """

    def __init__(
        self,
        series: PriceSeries,
    ):
        self.series = series

    def history(
        self,
        period: int = 20,
        annualize: bool = True,
    ) -> list[Volatility]:

        df = self.series.dataframe.copy()

        returns = df["Close"].pct_change()

        volatility = returns.rolling(period).std()

        if annualize:
            volatility *= math.sqrt(252)

        result = []

        for dt, value in zip(
            df["Date"],
            volatility,
        ):

            if pd.isna(value):
                continue

            if isinstance(dt, pd.Timestamp):
                dt = dt.date()

            result.append(
                Volatility(
                    date=dt,
                    volatility=float(value),
                )
            )

        return result

    def latest(
        self,
        period: int = 20,
        annualize: bool = True,
    ) -> Volatility | None:

        history = self.history(
            period=period,
            annualize=annualize,
        )

        if not history:
            return None

        return history[-1]

    def average(
        self,
        period: int = 20,
        annualize: bool = True,
    ) -> float | None:

        history = self.history(
            period=period,
            annualize=annualize,
        )

        if not history:
            return None

        return (
            sum(
                x.volatility
                for x in history
            )
            / len(history)
        )