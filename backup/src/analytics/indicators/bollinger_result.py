from dataclasses import dataclass

from src.models.bollinger_band import BollingerBand


@dataclass(slots=True)
class BollingerResult:
    """
    Result returned by BollingerCalculator.
    """

    name: str

    value: BollingerBand | None

    series: list[BollingerBand]

    signal: str | None = None

    interpretation: str | None = None