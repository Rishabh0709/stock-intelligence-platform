import pandas_ta as ta

from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)
from src.models.macd import MACD


class MACDCalculator(BaseIndicatorCalculator):
    """
    Calculates MACD indicator.
    """

    def macd(
    self,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> list[MACD]:

        df = self.dataframe

        macd_df = ta.macd(
        close=df["Close"],
        fast=fast,
        slow=slow,
        signal=signal,
        )
        
        if macd_df is None or macd_df.empty:
            return []

        macd_col = next(c for c in macd_df.columns if c.startswith("MACD_"))
        histogram_col = next(c for c in macd_df.columns if c.startswith("MACDh_"))
        signal_col = next(c for c in macd_df.columns if c.startswith("MACDs_"))

        result = []

        for i, row in macd_df.iterrows():

            result.append(
            MACD(
                date=self.normalize_date(df.loc[i, "Date"]),
                macd=self.to_float(row[macd_col]),
                signal=self.to_float(row[signal_col]),
                histogram=self.to_float(row[histogram_col]),
            )
            )

        return result

    def latest(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> MACD | None:

        history = self.macd(
            fast,
            slow,
            signal,
        )

        if not history:
            return None

        return history[-1]