from dataclasses import dataclass

from src.scoring.dto.score_result import ScoreResult


@dataclass(slots=True)
class StockScore:
    """
    Overall stock score.
    """

    score: int

    max_score: int

    results: list[ScoreResult]

    @property
    def normalized_score(self) -> float:
        """
        Converts score from [-max_score, +max_score]
        into [0, 100].

        -max_score -> 0
        0          -> 50
        +max_score -> 100
        """

        if self.max_score == 0:
            return 50.0

        return round(
            ((self.score + self.max_score) / (2 * self.max_score)) * 100,
            2,
        )

    @property
    def percentage(self) -> float:
        """
        Backward-compatible alias.
        """

        return self.normalized_score