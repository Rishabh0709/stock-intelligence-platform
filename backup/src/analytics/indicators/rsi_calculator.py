import pandas as pd
import pandas_ta as ta

from src.analytics.indicators.base_indicator_calculator import (
    BaseIndicatorCalculator,
)
from src.analytics.core.price_series import PriceSeries
from src.models.rsi import RSI


class RSICalculator(BaseIndicatorCalculator):

    def __init__(
        self,
        series: PriceSeries,
    ):
        super().__init__(series)

    def rsi(
        self,
        period: int = 14,
    ) -> list[RSI]:
        if period <= 0:
            raise ValueError("RSI period must be greater than zero")

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

        # pandas-ta needs more observations than the RSI period to produce
        # at least one usable value.
        if len(calculation_df) <= period:
            return []

        try:
            values = ta.rsi(
                calculation_df["Close"],
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

        # pandas-ta returns None when the input cannot produce an RSI series.
        if values is None or values.empty:
            return []

        return [
            RSI(
                date=self.normalize_date(dt),
                rsi=self.to_float(value),
            )
            for dt, value in zip(calculation_df["Date"], values)
        ]

    def latest(
        self,
        period: int = 14,
    ) -> float | None:

        history = self.rsi(period)

        return next(
            (
                row.rsi
                for row in reversed(history)
                if row.rsi is not None
            ),
            None,
        )
