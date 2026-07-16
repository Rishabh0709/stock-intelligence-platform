from abc import ABC, abstractmethod


class IPriceProvider(ABC):

    @abstractmethod
    def get_price_history(
        self,
        symbol: str,
        start_date,
        end_date,
    ):
        pass