import pandas as pd
import pandas_ta as ta

from src.analytics.providers.technical_indicator_provider import (
    TechnicalIndicatorProvider,
)


class PandasTAProvider(
    TechnicalIndicatorProvider,
):
    """
    pandas-ta implementation of the
    TechnicalIndicatorProvider interface.
    """

    def rsi(
        self,
        dataframe: pd.DataFrame,
        period: int,
    ) -> pd.Series:

        return ta.rsi(
            dataframe["Adj Close"],
            length=period,
        )

    def macd(
        self,
        dataframe: pd.DataFrame,
        fast: int,
        slow: int,
        signal: int,
    ) -> pd.DataFrame:

        return ta.macd(
            dataframe["Adj Close"],
            fast=fast,
            slow=slow,
            signal=signal,
        )

    def atr(
        self,
        dataframe: pd.DataFrame,
        period: int,
    ) -> pd.Series:

        return ta.atr(
            high=dataframe["High"],
            low=dataframe["Low"],
            close=dataframe["Adj Close"],
            length=period,
        )

    def adx(
        self,
        dataframe: pd.DataFrame,
        period: int,
    ) -> pd.DataFrame:

        return ta.adx(
            high=dataframe["High"],
            low=dataframe["Low"],
            close=dataframe["Adj Close"],
            length=period,
        )

    def bollinger(
        self,
        dataframe: pd.DataFrame,
        window: int,
        std: float,
    ) -> pd.DataFrame:

        return ta.bbands(
            dataframe["Adj Close"],
            length=window,
            std=std,
        )