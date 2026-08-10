from __future__ import annotations

from datetime import date, timedelta
import unittest

from src.models.company import Company
from src.models.daily_price import DailyPrice
from src.services.stock_intelligence_service import StockIntelligenceService


class CompanyRepositoryStub:
    def __init__(self, company):
        self.company = company

    def get(self, company_id):
        return self.company if company_id == self.company.id else None


class PriceRepositoryStub:
    def __init__(self, prices):
        self.prices = prices

    def list_by_company(self, company_id):
        return self.prices


def make_prices(rows=260):
    prices = []
    start = date.today() - timedelta(days=rows - 1)
    for index in range(rows):
        close = 100 + index * 0.2
        prices.append(
            DailyPrice(
                company_id=1,
                price_date=start + timedelta(days=index),
                open_price=close - 0.5,
                high_price=close + 1,
                low_price=close - 1,
                close_price=close,
                adjusted_close=close,
                volume=1000 + index * 5,
            )
        )
    return prices


class StockIntelligenceServiceTests(unittest.TestCase):
    def test_builds_complete_indicator_frame_and_report(self):
        company = Company(id=1, symbol="TEST", company_name="Test Ltd")
        service = StockIntelligenceService(
            CompanyRepositoryStub(company),
            PriceRepositoryStub(make_prices()),
        )
        result = service.analyze(1, account_capital=100_000)
        required = {
            "SMA_50", "SMA_200", "EMA_20", "EMA_50", "ATR_14", "ADX_14",
            "Plus_DI_14", "Minus_DI_14", "RSI_14", "MACD", "MACD_Signal",
            "MACD_Histogram", "BB_Upper", "BB_Lower", "OBV",
            "VWAP_Daily", "VWAP_Weekly",
        }
        self.assertTrue(required.issubset(result.indicator_frame.columns))
        self.assertEqual(result.report.symbol, "TEST")
        self.assertEqual(result.history_rows, 260)
        self.assertFalse(result.is_stale)
        self.assertIsNotNone(result.report.risk)

    def test_rejects_insufficient_history_without_crashing_engine(self):
        company = Company(id=1, symbol="SHORT", company_name="Short Ltd")
        service = StockIntelligenceService(
            CompanyRepositoryStub(company),
            PriceRepositoryStub(make_prices(20)),
        )
        with self.assertRaisesRegex(ValueError, "at least 35"):
            service.analyze(1, account_capital=100_000)


if __name__ == "__main__":
    unittest.main()
