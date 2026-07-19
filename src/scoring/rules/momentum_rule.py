from src.analysis.stock_analyzer import StockAnalyzer

from src.scoring.dto.score_result import ScoreResult
from src.scoring.rules.base_rule import ScoreRule

from src.scoring.score_weights import (
    BULLISH_MACD,
    BEARISH_MACD,
    RSI_HEALTHY,
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
    NEUTRAL_MOMENTUM,
)



class MomentumRule(ScoreRule):

    MAX_SCORE = 20
    
    def evaluate(
        self,
        analysis: StockAnalyzer,
    ) -> ScoreResult:

        momentum = analysis.momentum.analyze()

        score = 0
        reasons = []

        # MACD
        if momentum.bullish_macd:
            score += BULLISH_MACD
            reasons.append("Bullish MACD")

        elif momentum.bearish_macd:
            score += BEARISH_MACD
            reasons.append("Bearish MACD")

        # RSI
        if 50 <= momentum.rsi <= 70:
            score += RSI_HEALTHY
            reasons.append("Healthy RSI")

        elif momentum.rsi > 70:
            score += RSI_OVERBOUGHT
            reasons.append("Overbought RSI")

        elif momentum.rsi < 30:
            score += RSI_OVERSOLD
            reasons.append("Oversold RSI")

        return ScoreResult(
            rule="Momentum",
            points=score,
            passed=score > 0,
            reason=", ".join(reasons) if reasons else "Neutral Momentum",
        )