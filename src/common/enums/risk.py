from enum import StrEnum


class RiskLevel(StrEnum):
    """
    Overall investment risk.
    """

    LOW = "Low"

    MEDIUM = "Medium"

    HIGH = "High"


class DrawdownLevel(StrEnum):
    """
    Current drawdown severity.
    """

    HEALTHY = "Healthy"

    NORMAL = "Normal"

    DEEP = "Deep"

    SEVERE = "Severe"