import pandas as pd
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
        if period <= 0:
            raise ValueError(
                "Bollinger Band period must be greater than zero"
            )

        if std <= 0:
            raise ValueError(
                "Bollinger Band standard deviation must be greater than zero"
            )

        df = self.dataframe

        if df.empty or not {"Date", "Close"}.issubset(df.columns):
            return []

        calculation_df = df[["Date", "Close"]].copy()
        calculation_df["Close"] = pd.to_numeric(
            calculation_df["Close"],
            errors="coerce",
        )
        calculation_df = calculation_df.dropna(
            subset=["Date", "Close"],
        )

        if len(calculation_df) < period:
            return []

        try:
            bb = ta.bbands(
                close=calculation_df["Close"],
                length=period,
                std=std,
            )
        except (
            IndexError,
            KeyError,
            TypeError,
            ValueError,
            ZeroDivisionError,
        ):
            return []

        # pandas-ta returns None when the input cannot produce bands.
        if bb is None or bb.empty:
            return []

        lower_col = next(
            (column for column in bb.columns if column.startswith("BBL")),
            None,
        )
        middle_col = next(
            (column for column in bb.columns if column.startswith("BBM")),
            None,
        )
        upper_col = next(
            (column for column in bb.columns if column.startswith("BBU")),
            None,
        )

        if None in (lower_col, middle_col, upper_col):
            return []

        result = []

        for index, row in bb.iterrows():
            if index not in calculation_df.index:
                continue

            result.append(
                BollingerBand(
                    date=self.normalize_date(
                        calculation_df.loc[index, "Date"]
                    ),
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

        return next(
            (
                row
                for row in reversed(history)
                if (
                    row.upper is not None
                    and row.middle is not None
                    and row.lower is not None
                )
            ),
            None,
        )
