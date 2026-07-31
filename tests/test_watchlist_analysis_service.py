import unittest
from datetime import date, timedelta

from src.analytics.core.price_series import PriceSeries
from src.dto.snapshot_dto import SnapshotDTO
from src.models.company import Company
from src.models.daily_price import DailyPrice
from src.models.stock_data import StockData
from src.services.watchlist_analysis_service import WatchlistAnalysisService


class FakeStockExplorerService:
    def get_stock(self, symbol):
        prices = []
        start = date(2025, 7, 1)
        for index in range(260):
            value = 100 + index
            prices.append(
                DailyPrice(
                    company_id=1,
                    price_date=start + timedelta(days=index * 2),
                    open_price=value,
                    high_price=value + 1,
                    low_price=value - 1,
                    close_price=value,
                    adjusted_close=value,
                    volume=1_000 + index,
                )
            )

        return StockData(
            company=Company(
                id=1,
                symbol=symbol,
                company_name=f"{symbol} Limited",
                sector="Technology",
            ),
            price_series=PriceSeries(prices),
        )


class FakeProvider:
    def get_snapshot(self, symbol):
        return SnapshotDTO(
            symbol=symbol,
            current_price=360,
            previous_close=358,
            market_cap=1_000_000,
            trailing_pe=25,
            forward_pe=22,
            price_to_book=4,
            dividend_yield=0.01,
        )


class WatchlistAnalysisServiceTest(unittest.TestCase):
    def test_builds_quantitative_review_and_watchlist_signals(self):
        service = WatchlistAnalysisService(
            stock_explorer_service=FakeStockExplorerService(),
            provider=FakeProvider(),
        )

        result = service.analyze(
            "TEST",
            entry_price=300,
            target_price=350,
            alert_price=280,
        )

        self.assertEqual(result.symbol, "TEST")
        self.assertEqual(result.current_price, 360)
        self.assertEqual(result.technical["50_day_moving_average"], 334.5)
        self.assertEqual(result.technical["200_day_moving_average"], 259.5)
        self.assertEqual(len(result.price_history), 253)
        self.assertIn(
            "The saved target price has been reached.",
            result.signals,
        )
        self.assertIsNotNone(result.returns_percent["1_year"])
        self.assertIsNotNone(result.risk["annualized_volatility_1y"])


if __name__ == "__main__":
    unittest.main()
