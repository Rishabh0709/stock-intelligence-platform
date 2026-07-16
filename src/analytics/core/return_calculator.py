from src.analytics.core.price_series import PriceSeries


class ReturnCalculator:
    """
    Calculates return-based performance metrics for a PriceSeries.

    All return values are expressed as decimals.

    Example:
        0.10 = 10%
        -0.05 = -5%
    """

    def __init__(
        self,
        series: PriceSeries,
    ):
        self.series = series

    def daily_return(self) -> float | None:
        """
        Returns the latest one-day return.
        """

        if self.series.count() < 2:
            return None

        closes = self.series.close_prices

        previous = closes[-2]
        latest = closes[-1]

        return (latest - previous) / previous

    def total_return(self) -> float | None:
        """
        Returns the total return over the available history.
        """

        if self.series.count() < 2:
            return None

        first = self.series.first()
        latest = self.series.latest()

        return (
            latest.close_price - first.close_price
        ) / first.close_price

    def annualized_return(self) -> float | None:
        """
        Calculates the annualized return (CAGR).
        """

        if self.series.count() < 2:
            return None

        first = self.series.first()
        latest = self.series.latest()

        days = (latest.price_date - first.price_date).days

        if days <= 0:
            return None

        years = days / 365.25

        return (
            (latest.close_price / first.close_price)
            ** (1 / years)
        ) - 1

    def cagr(self) -> float | None:
        """
        Alias for annualized_return().
        """

        return self.annualized_return()