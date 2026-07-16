import pandas_ta as ta

from src.analytics.constants import (
    DEFAULT_BOLLINGER_STD,
    DEFAULT_BOLLINGER_WINDOW,
)
from src.analytics.indicators.indicator_base import IndicatorBase
from src.analytics.indicator_result import IndicatorResult
from src.models.bollinger import BollingerBand


class BollingerCalculator(IndicatorBase):
    """
    Calculates Bollinger Bands.
    """

    def __init__(
        self,
        series,
        window: int = DEFAULT_BOLLINGER_WINDOW,
        std: float = DEFAULT_BOLLINGER_STD,
    ):
        super().__init__(series)

        self.window = window
        self.std = std

    # ==========================================================
    # Series
    # ==========================================================

    def bollinger_series(
        self,
    ) -> list[BollingerBand]:

        if not self.has_enough_data(self.window):
            return [
            BollingerBand(
            date=date,
            upper=None,
            middle=None,
            lower=None,
            )
            for date in self.series.dates
            ]
        
        df = ta.bbands(
            close=self.dataframe["Adj Close"],
            length=self.window,
            std=self.std,
        )

        #
        # pandas-ta returns:
        #   0 -> Lower Band
        #   1 -> Middle Band
        #   2 -> Upper Band
        #   3 -> Bandwidth
        #   4 -> Percent B
        #

        lower_values = self.pandas_to_list(
            df.iloc[:, 0]
        )

        middle_values = self.pandas_to_list(
            df.iloc[:, 1]
        )

        upper_values = self.pandas_to_list(
            df.iloc[:, 2]
        )

        history: list[BollingerBand] = []

        for (
            date,
            upper,
            middle,
            lower,
        ) in zip(
            self.series.dates,
            upper_values,
            middle_values,
            lower_values,
        ):

            history.append(
                BollingerBand(
                    date=date,
                    upper=upper,
                    middle=middle,
                    lower=lower,
                )
            )

        return history

    # ==========================================================
    # Signal
    # ==========================================================

    def _signal(
        self,
        band: BollingerBand | None,
    ) -> str | None:

        close = self.series.latest_adjusted_close()

        if (
            band is None
            or close is None
            or band.upper is None
            or band.lower is None
        ):
            return None

        if close > band.upper:
            return "SELL"

        if close < band.lower:
            return "BUY"

        return "HOLD"

    def _interpretation(
        self,
        band: BollingerBand | None,
    ) -> str | None:

        close = self.series.latest_adjusted_close()

        if (
            band is None
            or close is None
            or band.upper is None
            or band.lower is None
        ):
            return None

        if close > band.upper:
            return "Price above upper band"

        if close < band.lower:
            return "Price below lower band"

        return "Price within bands"

    # ==========================================================
    # Public API
    # ==========================================================

    def calculate(
        self,
    ) -> IndicatorResult[BollingerBand]:

        history = self.bollinger_series()

        latest = self.latest(
            history,
        )

        return self.create_result(
            name=f"BB({self.window},{self.std})",
            history=history,
            signal=self._signal(latest),
            interpretation=self._interpretation(latest),
        )

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    def bollinger(
        self,
    ) -> IndicatorResult[BollingerBand]:

        return self.calculate()