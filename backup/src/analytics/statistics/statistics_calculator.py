from collections.abc import Callable
from math import sqrt


class StatisticsCalculator:
    """
    Generic statistical calculator.

    This class intentionally knows nothing about stocks,
    prices, indicators, or finance.

    It operates on any numeric series and provides reusable
    statistical functions for analytics throughout the project.
    """

    def __init__(
        self,
        values: list[float],
    ):

        if not values:
            raise ValueError(
                "Values cannot be empty."
            )

        self.values = values

    # ==========================================================
    # Generic Rolling Engine
    # ==========================================================

    def _rolling(
        self,
        window: int,
        calculation: Callable[[list[float]], float],
    ) -> list[float | None]:
        """
        Applies a calculation over a rolling window.
        """

        if window <= 0:
            raise ValueError(
                "Window must be positive."
            )

        result = []

        for index in range(len(self.values)):

            if index + 1 < window:
                result.append(None)
                continue

            subset = self.values[
                index - window + 1:
                index + 1
            ]

            result.append(
                calculation(subset)
            )

        return result

    # ==========================================================
    # Mean
    # ==========================================================

    @staticmethod
    def mean(
        values: list[float],
    ) -> float:

        if not values:
            raise ValueError(
                "Cannot calculate mean of an empty series."
            )

        return sum(values) / len(values)

    # ==========================================================
    # Variance
    # ==========================================================

    @staticmethod
    def variance(
        values: list[float],
    ) -> float:

        if len(values) < 2:
            raise ValueError(
                "Variance requires at least two observations."
            )

        avg = StatisticsCalculator.mean(values)

        return sum(
            (value - avg) ** 2
            for value in values
        ) / len(values)

    # ==========================================================
    # Standard Deviation
    # ==========================================================

    @staticmethod
    def std(
        values: list[float],
    ) -> float:

        return sqrt(
            StatisticsCalculator.variance(values)
        )

    # ==========================================================
    # Rolling Mean
    # ==========================================================

    def rolling_mean(
        self,
        window: int,
    ) -> list[float | None]:

        return self._rolling(
            window,
            self.mean,
        )

    # ==========================================================
    # Rolling Variance
    # ==========================================================

    def rolling_variance(
        self,
        window: int,
    ) -> list[float | None]:

        return self._rolling(
            window,
            self.variance,
        )

    # ==========================================================
    # Rolling Standard Deviation
    # ==========================================================

    def rolling_std(
        self,
        window: int,
    ) -> list[float | None]:

        return self._rolling(
            window,
            self.std,
        )

    # ==========================================================
    # Latest Statistics
    # ==========================================================

    def latest_mean(
        self,
        window: int,
    ) -> float | None:

        return self.rolling_mean(window)[-1]

    def latest_variance(
        self,
        window: int,
    ) -> float | None:

        return self.rolling_variance(window)[-1]

    def latest_std(
        self,
        window: int,
    ) -> float | None:

        return self.rolling_std(window)[-1]