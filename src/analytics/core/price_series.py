from __future__ import annotations

import math
from datetime import date

import pandas as pd

from src.models.daily_price import DailyPrice


class PriceSeries:
    """
    Represents historical price data.

    Provides convenient access to prices, returns,
    statistics and pandas DataFrame conversion for
    analytics.
    """

    def __init__(
        self,
        prices: list[DailyPrice],
    ):
        self._prices = sorted(
            prices,
            key=lambda p: p.price_date,
        )

        #
        # Lazily created DataFrame.
        #

        self._dataframe: pd.DataFrame | None = None

    # ==========================================================
    # Basic Properties
    # ==========================================================

    @property
    def prices(self) -> list[DailyPrice]:
        return self._prices

    @property
    def dates(self) -> list[date]:
        return [
            p.price_date
            for p in self._prices
        ]

    @property
    def open_prices(self) -> list[float | None]:
        return [
            p.open_price
            for p in self._prices
        ]

    @property
    def high_prices(self) -> list[float | None]:
        return [
            p.high_price
            for p in self._prices
        ]

    @property
    def low_prices(self) -> list[float | None]:
        return [
            p.low_price
            for p in self._prices
        ]

    @property
    def close_prices(self) -> list[float | None]:
        return [
            p.close_price
            for p in self._prices
        ]

    @property
    def adjusted_close_prices(self) -> list[float | None]:
        return [
            p.adjusted_close
            for p in self._prices
        ]

    @property
    def volumes(self) -> list[int | None]:
        return [
            p.volume
            for p in self._prices
        ]

    # ==========================================================
    # DataFrame
    # ==========================================================

    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the series into a pandas DataFrame.

        Suitable for libraries such as pandas-ta.
        """

        return pd.DataFrame(
            {
                "Date": self.dates,
                "Open": self.open_prices,
                "High": self.high_prices,
                "Low": self.low_prices,
                "Close": self.close_prices,
                "Adj Close": self.adjusted_close_prices,
                "Volume": self.volumes,
            }
        )

    @property
    def dataframe(self) -> pd.DataFrame:
        """
        Cached DataFrame representation.
        """

        if self._dataframe is None:

            self._dataframe = (
                self.to_dataframe()
            )

        return self._dataframe

    # ==========================================================
    # Convenience Methods
    # ==========================================================

    def count(self) -> int:
        return len(self._prices)

    def is_empty(self) -> bool:
        return self.count() == 0

    def first(self) -> DailyPrice | None:
        return (
            self._prices[0]
            if self._prices
            else None
        )

    def latest(self) -> DailyPrice | None:
        return (
            self._prices[-1]
            if self._prices
            else None
        )

    # ==========================================================
    # Latest Values
    # ==========================================================

    def latest_close(self) -> float | None:

        latest = self.latest()

        return (
            latest.close_price
            if latest
            else None
        )

    def latest_adjusted_close(self) -> float | None:

        latest = self.latest()

        return (
            latest.adjusted_close
            if latest
            else None
        )

    def latest_open(self) -> float | None:

        latest = self.latest()

        return (
            latest.open_price
            if latest
            else None
        )

    def latest_high(self) -> float | None:

        latest = self.latest()

        return (
            latest.high_price
            if latest
            else None
        )

    def latest_low(self) -> float | None:

        latest = self.latest()

        return (
            latest.low_price
            if latest
            else None
        )

    def latest_volume(self) -> int | None:

        latest = self.latest()

        return (
            latest.volume
            if latest
            else None
        )

    def latest_date(self) -> date | None:

        latest = self.latest()

        return (
            latest.price_date
            if latest
            else None
        )

    def oldest_date(self) -> date | None:

        first = self.first()

        return (
            first.price_date
            if first
            else None
        )

    # ==========================================================
    # Returns
    # ==========================================================

    def daily_returns(
        self,
    ) -> list[float]:

        """
        Daily percentage returns using adjusted close.
        """

        prices = [
            p
            for p in self.adjusted_close_prices
            if p is not None
        ]

        returns = []

        for previous, current in zip(
            prices[:-1],
            prices[1:],
        ):

            if previous <= 0:
                continue

            returns.append(
                (current - previous)
                / previous
            )

        return returns

    def log_returns(
        self,
    ) -> list[float]:

        """
        Natural logarithmic returns.
        """

        prices = [
            p
            for p in self.adjusted_close_prices
            if p is not None
        ]

        returns = []

        for previous, current in zip(
            prices[:-1],
            prices[1:],
        ):

            if previous <= 0:
                continue

            returns.append(
                math.log(
                    current / previous
                )
            )

        return returns

    # ==========================================================
    # Range Operations
    # ==========================================================

    def last(
        self,
        periods: int,
    ) -> "PriceSeries":
        """
        Returns last N observations.
        """

        return PriceSeries(
            self._prices[-periods:]
        )

    def between(
        self,
        start: date,
        end: date,
    ) -> "PriceSeries":
        """
        Returns prices between two dates.
        """

        return PriceSeries(
            [
                p
                for p in self._prices
                if start <= p.price_date <= end
            ]
        )