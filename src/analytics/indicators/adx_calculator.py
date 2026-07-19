import pandas_ta as ta

from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)
from src.models.adx import ADX


class ADXCalculator(BaseIndicatorCalculator):
    """
    Calculates Average Directional Index (ADX).
    """

    def adx(
        self,
        period: int = 14,
    ) -> list[ADX]:

        df = self.dataframe

        adx = ta.adx(
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            length=period,
        )

        result = []

        adx_col = next(c for c in adx.columns if c.startswith("ADX_"))
        dmp_col = next(c for c in adx.columns if c.startswith("DMP_"))
        dmn_col = next(c for c in adx.columns if c.startswith("DMN_"))

        result = []

        for _, row in adx.iterrows():

            result.append(
            ADX(
            date=self.normalize_date(df.loc[row.name, "Date"]),
            plus_di=self.to_float(row[dmp_col]),
            minus_di=self.to_float(row[dmn_col]),
            adx=self.to_float(row[adx_col]),
            )
            )

        return result

    def latest(
        self,
        period: int = 14,
    ) -> ADX | None:

        history = self.adx(period)

        if not history:
            return None

        return history[-1]