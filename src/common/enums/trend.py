from enum import StrEnum

class Trend(StrEnum):
    """
    Overall market trend.
    """

    BULLISH = "Bullish"

    BEARISH = "Bearish"

    NEUTRAL = "Neutral"


class TrendStrength(StrEnum):
    """
    Strength of the detected trend.
    """

    STRONG = "Strong"

    MODERATE = "Moderate"

    WEAK = "Weak"

    UNKNOWN = "Unknown"