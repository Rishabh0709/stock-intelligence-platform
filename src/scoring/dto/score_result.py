from dataclasses import dataclass


@dataclass(slots=True)
class ScoreResult:
    """
    Result produced by a single scoring rule.
    """

    rule: str

    points: int

    passed: bool

    reason: str