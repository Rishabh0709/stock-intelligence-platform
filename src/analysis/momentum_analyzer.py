from src.models.stock_data import StockData

from src.analysis.dto.momentum_analysis import MomentumAnalysis

from src.analytics.indicators.rsi_calculator import RSICalculator
from src.analytics.indicators.macd_calculator import MACDCalculator

from src.common.enums.momentum import Momentum



class MomentumAnalyzer:

    def __init__(
        self,
        stock: StockData,
    ):
        self.stock = stock

        self.series = stock.price_series

        self.rsi = RSICalculator(self.series)

        self.macd = MACDCalculator(self.series)

    def analyze(self) -> MomentumAnalysis:

        latest_rsi = self.rsi.latest()

        latest_macd = self.macd.latest()

        rsi = (
            latest_rsi
            if latest_rsi
            else None
        )

        macd = (
            latest_macd.macd
            if latest_macd
            else None
        )

        signal = (
            latest_macd.signal
            if latest_macd
            else None
        )

        histogram = (
            latest_macd.histogram
            if latest_macd
            else None
        )

        return MomentumAnalysis(

            date=self.series.latest_date(),

            momentum=self._classify(
                rsi,
                macd,
                signal,
            ),

            rsi=rsi,

            macd=macd,

            signal=signal,

            histogram=histogram,

            bullish_macd=(
                macd is not None
                and signal is not None
                and macd > signal
            ),

            bearish_macd=(
                macd is not None
                and signal is not None
                and macd < signal
            ),

            overbought=(
                rsi is not None
                and rsi >= 70
            ),

            oversold=(
                rsi is not None
                and rsi <= 30
            ),
        )

    def _classify(
        self,
        rsi,
        macd,
        signal,
    ) -> str:

        if None in (rsi, macd, signal):
            return Momentum.NEUTRAL

        if macd > signal and rsi > 55:
            return Momentum.BULLISH

        if macd < signal and rsi < 45:
            return Momentum.BEARISH

        return Momentum.NEUTRAL