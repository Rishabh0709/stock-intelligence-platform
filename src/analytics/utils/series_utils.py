from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class SeriesUtils:
    """
    Utility methods for working with indicator series.

    These helpers are shared across all technical indicators.
    """

    @staticmethod
    def latest_valid(
        series: list[T],
        validator: Callable[[T], bool] | None = None,
    ) -> T | None:
        """
        Returns the latest valid value in a series.

        If no validator is provided, None values are ignored.
        """

        if validator is None:

            validator = lambda value: value is not None

        for value in reversed(series):

            if validator(value):
                return value

        return None

    @staticmethod
    def first_valid(
        series: list[T],
        validator: Callable[[T], bool] | None = None,
    ) -> T | None:
        """
        Returns the first valid value.
        """

        if validator is None:

            validator = lambda value: value is not None

        for value in series:

            if validator(value):
                return value

        return None

    @staticmethod
    def last_n_valid(
        series: list[T],
        count: int,
        validator: Callable[[T], bool] | None = None,
    ) -> list[T]:
        """
        Returns the latest N valid observations.
        """

        if count <= 0:
            raise ValueError(
                "Count must be positive."
            )

        if validator is None:

            validator = lambda value: value is not None

        result = []

        for value in reversed(series):

            if validator(value):

                result.append(value)

                if len(result) == count:
                    break

        return list(reversed(result))