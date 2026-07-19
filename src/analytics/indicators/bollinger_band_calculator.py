import pandas_ta as ta

from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)
from src.models.bollinger_band import BollingerBand


class BollingerBandCalculator(BaseIndicatorCalculator):
    """
    Calculates Bollinger Bands.
    """

    def bands(
        self,
        period: int = 20,
        std: float = 2.0,
    ) -> list[BollingerBand]:

        df = self.dataframe

        bb = ta.bbands(
            close=df["Close"],
            length=period,
            std=std,
        )

        lower_col = next(c for c in bb.columns if c.startswith("BBL"))
        middle_col = next(c for c in bb.columns if c.startswith("BBM"))
        upper_col = next(c for c in bb.columns if c.startswith("BBU"))

        result = []

        for i, row in bb.iterrows():

            result.append(
                BollingerBand(
                    date=self.normalize_date(df.loc[i, "Date"]),
                    upper=self.to_float(row[upper_col]),
                    middle=self.to_float(row[middle_col]),
                    lower=self.to_float(row[lower_col]),
                )
            )

        return result

    def latest(
        self,
        period: int = 20,
        std: float = 2.0,
    ) -> BollingerBand | None:

        history = self.bands(period, std)

        if not history:
            return None

        return history[-1]