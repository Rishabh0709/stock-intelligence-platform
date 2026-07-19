import pandas as pd

from src.analytics.core.price_series import PriceSeries
from src.models.drawdown import Drawdown


class DrawdownCalculator:
    """
    Calculates drawdown statistics.
    """

    def __init__(
        self,
        series: PriceSeries,
    ):
        self.series = series

    def historical(self) -> list[Drawdown]:

        df = self.series.dataframe.copy()

        close = df["Close"]

        running_max = close.cummax()

        drawdowns = (close - running_max) / running_max

        result = []

        for dt, value in zip(df["Date"], drawdowns):

            if isinstance(dt, pd.Timestamp):
                dt = dt.date()

            result.append(
                Drawdown(
                    date=dt,
                    drawdown=(
                        None
                        if pd.isna(value)
                        else float(value)
                    ),
                )
            )

        return result

    def latest(self) -> float | None:

        history = self.historical()

        if not history:
            return None

        return history[-1].drawdown

    def maximum(self) -> float | None:

        values = [
            x.drawdown
            for x in self.historical()
            if x.drawdown is not None
        ]

        if not values:
            return None

        return min(values)