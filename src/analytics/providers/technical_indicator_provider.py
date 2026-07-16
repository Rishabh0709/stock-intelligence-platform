from abc import ABC, abstractmethod

import pandas as pd


class TechnicalIndicatorProvider(ABC):
    """
    Base interface for technical analysis providers.

    Implementations may wrap:
    - pandas-ta
    - TA-Lib
    - vectorbt
    """

    @abstractmethod
    def rsi(
        self,
        dataframe: pd.DataFrame,
        period: int,
    ) -> pd.Series:
        pass

    @abstractmethod
    def macd(
        self,
        dataframe: pd.DataFrame,
        fast: int,
        slow: int,
        signal: int,
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def atr(
        self,
        dataframe: pd.DataFrame,
        period: int,
    ) -> pd.Series:
        pass

    @abstractmethod
    def adx(
        self,
        dataframe: pd.DataFrame,
        period: int,
    ) -> pd.DataFrame:
        pass

    @abstractmethod
    def bollinger(
        self,
        dataframe: pd.DataFrame,
        window: int,
        std: float,
    ) -> pd.DataFrame:
        pass