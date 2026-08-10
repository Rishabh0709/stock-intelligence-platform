from dataclasses import dataclass


@dataclass(slots=True)
class ImportedHolding:
    """
    Represents a holding imported from a broker statement.

    This object is broker-specific and exists only during import.
    It is later converted into PortfolioHolding.
    """

    symbol: str

    isin: str

    quantity: float

    average_price: float