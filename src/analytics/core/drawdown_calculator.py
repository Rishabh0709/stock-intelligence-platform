from src.analytics.core.price_series import PriceSeries


class DrawdownCalculator:
    """
    Calculates drawdown statistics.

    Drawdown measures decline from previous peak.

    Example

    Peak = 100

    Current = 80

    Drawdown = -20%
    """

    def __init__(
        self,
        series: PriceSeries,
    ):
        self.series = series

    def drawdown_series(self) -> list[float]:
        """
        Returns drawdown for every trading day.

        Values range from

        0.0      -> New High

        -0.15    -> 15% below previous peak
        """

        prices = [
            price.adjusted_close
            for price in self.series.prices
            if price.adjusted_close is not None
        ]

        if not prices:
            return []

        peak = prices[0]

        drawdowns = []

        for price in prices:

            if price > peak:
                peak = price

            drawdown = (price - peak) / peak

            drawdowns.append(drawdown)

        return drawdowns

    def maximum_drawdown(self) -> float | None:
        """
        Returns worst historical drawdown.

        Example

        -0.42 = -42%
        """

        drawdowns = self.drawdown_series()

        if not drawdowns:
            return None

        return min(drawdowns)

    def current_drawdown(self) -> float | None:
        """
        Returns drawdown from latest price.

        Useful for dashboards.
        """

        drawdowns = self.drawdown_series()

        if not drawdowns:
            return None

        return drawdowns[-1]