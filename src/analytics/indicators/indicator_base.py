from abc import ABC
import math
from typing import Generic, TypeVar

import pandas as pd

from src.analytics.indicator_result import IndicatorResult
from src.analytics.core.price_series import PriceSeries

T = TypeVar("T")


class IndicatorBase(ABC):
    """
    Base class for all technical indicators.
    """

    def __init__(
        self,
        series: PriceSeries,
    ):
        self.series = series

    # ==========================================================
    # Data Access
    # ==========================================================

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Historical prices as a pandas DataFrame.
        """

        return self.series.dataframe

    @property
    def count(self) -> int:
        """
        Number of observations.
        """

        return self.series.count()

    # ==========================================================
    # Validation
    # ==========================================================

    def has_enough_data(
        self,
        periods: int,
    ) -> bool:
        """
        Checks whether sufficient historical
        data is available.
        """

        return self.count >= periods

    # ==========================================================
    # Pandas Helpers
    # ==========================================================

    @staticmethod
    def pandas_to_list(
        values: pd.Series,
    ) -> list[float | None]:
        """
        Converts a pandas Series into a Python list.

        NaN values are converted to None.
        """

        result: list[float | None] = []

        for value in values.tolist():

            if (
                value is None
                or (
                    isinstance(value, float)
                    and math.isnan(value)
                )
            ):
                result.append(None)

            else:
                result.append(float(value))

        return result

    @staticmethod
    def latest(
        values: list[T],
    ) -> T | None:
        """
        Returns the latest value in a series.
        """

        return values[-1] if values else None

    # ==========================================================
    # Result Builder
    # ==========================================================

    def create_result(
        self,
        *,
        name: str,
        history: list[T],
        signal: str | None = None,
        interpretation: str | None = None,
    ) -> IndicatorResult[T]:
        """
        Creates a standard IndicatorResult.
        """

        return IndicatorResult(
            name=name,
            latest=self.latest(history),
            history=history,
            signal=signal,
            interpretation=interpretation,
        )