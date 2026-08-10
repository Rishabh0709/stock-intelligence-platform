from src.providers.data_provider import IDataProvider
from src.providers.yahoo_provider import YahooProvider


class ProviderFactory:

    @staticmethod
    def create() -> IDataProvider:
        """
        Returns the configured market data provider.
        """

        return YahooProvider()