import pandas as pd
import pandas_ta as ta

from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)
from src.models.adx import ADX


class ADXCalculator(BaseIndicatorCalculator):
    """Calculates Average Directional Index (ADX)."""

    def adx(
        self,
        period: int = 14,
    ) -> list[ADX]:
        if period <= 0:
            raise ValueError("ADX period must be greater than zero")

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
            subset=["Date", "High", "Low", "Close"]
        )

        # ADX needs sufficient history to initialise its calculations.
        if len(calculation_df) < period * 2:
            return []

        try:
            adx_frame = ta.adx(
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

        # pandas-ta can return None when ADX cannot be calculated.
        if adx_frame is None or adx_frame.empty:
            return []

        adx_col = next(
            (
                column
                for column in adx_frame.columns
                if column.startswith("ADX_")
            ),
            None,
        )

        dmp_col = next(
            (
                column
                for column in adx_frame.columns
                if column.startswith("DMP_")
            ),
            None,
        )

        dmn_col = next(
            (
                column
                for column in adx_frame.columns
                if column.startswith("DMN_")
            ),
            None,
        )

        if None in (adx_col, dmp_col, dmn_col):
            return []

        result = []

        for index, row in adx_frame.iterrows():
            if index not in calculation_df.index:
                continue

            result.append(
                ADX(
                    date=self.normalize_date(
                        calculation_df.loc[index, "Date"]
                    ),
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

        return next(
            (
                row
                for row in reversed(history)
                if row.adx is not None
            ),
            None,
        )