import math
from math import sqrt

import statistics

from src.analytics.core.price_series import PriceSeries
from src.analytics.constants import TRADING_DAYS_PER_YEAR

from src.analytics.statistics.statistics_calculator import (
    StatisticsCalculator,
)

class VolatilityCalculator:
    """
    Calculates annualized historical volatility.

    Volatility is computed using daily percentage returns
    based on adjusted closing prices.
    """


    def __init__(
        self,
        series: PriceSeries,
    ):
        self.series = series

    def calculate(self) -> float | None:
        """
        Returns annualized volatility.

        Example
        -------
        0.21 = 21%
        """

        returns = self.series.daily_returns()

        if len(returns) < 2:
            return None

        stats = StatisticsCalculator(self.series.daily_returns())

        std = stats.standard_deviation()

        if std is None:
            return None

        return std * sqrt(self.TRADING_DAYS_PER_YEAR)

        