from abc import ABC
from abc import abstractmethod

from src.analysis.stock_analyzer import StockAnalyzer
from src.scoring.dto.score_result import ScoreResult


class ScoreRule(ABC):
    """
    Base class for all scoring rules.
    """

    MAX_SCORE: int = 0

    @abstractmethod
    def evaluate(
        self,
        analysis: StockAnalyzer,
    ) -> ScoreResult:
        pass