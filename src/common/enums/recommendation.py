from enum import StrEnum


class Recommendation(StrEnum):
    """
    Final investment recommendation.
    """

    STRONG_BUY = "Strong Buy"

    BUY = "Buy"

    ACCUMULATE = "Accumulate"

    HOLD = "Hold"

    REDUCE = "Reduce"

    SELL = "Sell"


class Confidence(StrEnum):
    """
    Confidence level of recommendation.
    """

    VERY_HIGH = "Very High"

    HIGH = "High"

    MODERATE = "Moderate"

    LOW = "Low"