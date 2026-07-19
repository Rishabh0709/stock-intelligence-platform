from abc import ABC, abstractmethod

from src.models.company import Company


class BaseCollector(ABC):

    @abstractmethod
    def get_company(self, symbol: str) -> Company:
        """
        Fetch company information from a data source.
        """
        pass