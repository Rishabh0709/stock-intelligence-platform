import pandas as pd
import pandas_ta as ta

from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)
from src.models.atr import ATR


class ATRCalculator(BaseIndicatorCalculator):
    """
    Calculates True Range and Average True Range.
    """

    def atr(
        self,
        period: int = 14,
    ) -> list[ATR]:
        if period <= 0:
            raise ValueError("ATR period must be greater than zero")

        df = self.dataframe

        required_columns = {"Date", "High", "Low", "Close"}

        if df.empty or not required_columns.issubset(df.columns):
            return []

        calculation_df = df[
            ["Date", "High", "Low", "Close"]
        ].copy()

        for column in ("High", "Low", "Close"):
            calculation_df[column] = pd.to_numeric(
                calculation_df[column],
                errors="coerce",
            )

        calculation_df = calculation_df.dropna(
            subset=["Date", "High", "Low", "Close"],
        )

        # ATR needs more observations than its period to initialise.
        if len(calculation_df) <= period:
            return []

        try:
            tr = ta.true_range(
                high=calculation_df["High"],
                low=calculation_df["Low"],
                close=calculation_df["Close"],
            )

            atr = ta.atr(
                high=calculation_df["High"],
                low=calculation_df["Low"],
                close=calculation_df["Close"],
                length=period,
            )
        except (
            IndexError,
            KeyError,
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):
            return []

        # pandas-ta returns None when the input cannot produce a series.
        if tr is None or atr is None or tr.empty or atr.empty:
            return []

        result = []

        for dt, tr_value, atr_value in zip(
            calculation_df["Date"],
            tr,
            atr,
        ):
            result.append(
                ATR(
                    date=self.normalize_date(dt),
                    true_range=self.to_float(tr_value),
                    atr=self.to_float(atr_value),
                )
            )

        return result

    def latest(
        self,
        period: int = 14,
    ) -> ATR | None:

        history = self.atr(period)

        return next(
            (
                row
                for row in reversed(history)
                if row.atr is not None
            ),
            None,
        )
