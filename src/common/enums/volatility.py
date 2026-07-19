from enum import StrEnum


class VolatilityLevel(StrEnum):
    """
    Historical volatility level.
    """

    LOW = "Low"

    MEDIUM = "Medium"

    HIGH = "High"


class BandPosition(StrEnum):
    """
    Position of price relative to Bollinger Bands.
    """

    ABOVE_UPPER = "Above Upper Band"

    NEAR_UPPER = "Near Upper Band"

    WITHIN = "Within Bands"

    NEAR_LOWER = "Near Lower Band"

    BELOW_LOWER = "Below Lower Band"