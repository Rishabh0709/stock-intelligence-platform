import unittest
from datetime import date

from src.analytics.core.price_series import PriceSeries
from src.models.daily_price import DailyPrice
from src.services.stock_intelligence_service import StockIntelligenceService


def price(*, close=100.0, adjusted_close=50.0):
    return DailyPrice(
        company_id=1,
        price_date=date(2026, 1, 2),
        open_price=90.0,
        high_price=110.0,
        low_price=80.0,
        close_price=close,
        adjusted_close=adjusted_close,
        volume=1_000,
    )


class MarketPriceContractTests(unittest.TestCase):
    def test_market_and_analysis_prices_are_explicit(self):
        bar = price()

        self.assertEqual(bar.market_price, 100.0)
        self.assertEqual(bar.analysis_price, 50.0)
        self.assertEqual(bar.adjustment_factor, 0.5)
        self.assertEqual(bar.analysis_open, 45.0)
        self.assertEqual(bar.analysis_high, 55.0)
        self.assertEqual(bar.analysis_low, 40.0)

    def test_invalid_adjusted_close_falls_back_to_raw_close(self):
        bar = price(adjusted_close=None)

        self.assertEqual(bar.analysis_price, 100.0)
        self.assertEqual(bar.adjustment_factor, 1.0)

    def test_price_series_dataframe_uses_adjusted_ohlc(self):
        frame = PriceSeries([price()]).to_dataframe()

        self.assertEqual(frame.loc[0, "Open"], 45.0)
        self.assertEqual(frame.loc[0, "Close"], 50.0)
        self.assertEqual(frame.loc[0, "Adj Close"], 50.0)

    def test_scanner_frame_preserves_market_close_separately(self):
        frame = StockIntelligenceService._build_indicator_frame([price()])

        self.assertEqual(frame.loc[0, "Close"], 50.0)
        self.assertEqual(frame.loc[0, "Market Close"], 100.0)


if __name__ == "__main__":
    unittest.main()
