from datetime import date

from src.analytics.core.price_series import PriceSeries
from src.analytics.constants import CALENDAR_DAYS_PER_YEAR


class CAGRCalculator:
    """
    Calculates Compound Annual Growth Rate (CAGR).

    CAGR normalizes returns over time and is useful for comparing
    investments held for different durations.
    """

    def __init__(
        self,
        series: PriceSeries,
    ):

        self.series = series

    def calculate(self) -> float | None:
        """
        Returns CAGR as a decimal.

        Example
        -------
        0.18 = 18%
        """

        if self.series.count() < 2:
            return None

        first = self.series.first()
        last = self.series.latest()

        if (
            first is None
            or last is None
            or first.adjusted_close is None
            or last.adjusted_close is None
        ):
            return None

        days = (last.price_date - first.price_date).days

        if days <= 0:
            return None

        years = days / CALENDAR_DAYS_PER_YEAR

        return (
            last.adjusted_close
            / first.adjusted_close
        ) ** (1 / years) - 1