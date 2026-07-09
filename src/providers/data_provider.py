from abc import ABC, abstractmethod
from datetime import date

import pandas as pd

from src.dto.company_dto import CompanyDTO
from src.dto.snapshot_dto import SnapshotDTO


class IDataProvider(ABC):

    """
    Base interface for every market data provider.
    """

    @abstractmethod
    def get_company(
        self,
        symbol: str
    ) -> CompanyDTO:
        pass

    @abstractmethod
    def get_snapshot(
        self,
        symbol: str
    ) -> SnapshotDTO:
        pass

    @abstractmethod
    def get_price_history(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> pd.DataFrame:
        pass