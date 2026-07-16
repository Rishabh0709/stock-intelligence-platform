from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class IndicatorResult(Generic[T]):
    """
    Represents the output of a technical indicator.
    """

    name: str

    latest: T | None

    history: list[T]

    signal: str | None = None

    interpretation: str | None = None