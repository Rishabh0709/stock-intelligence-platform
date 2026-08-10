import sys
import types
import unittest
from datetime import date, datetime

import pandas as pd


sys.modules.setdefault(
    "yfinance",
    types.SimpleNamespace(Ticker=lambda symbol: None),
)

from src.providers.yahoo_provider import YahooProvider


class FakeTicker:
    calendar = {
        "Earnings Date": [datetime(2026, 8, 20)],
        "Ex-Dividend Date": datetime(2026, 8, 25),
    }
    actions = pd.DataFrame(
        {
            "Dividends": [5.5, 0.0],
            "Stock Splits": [0.0, 2.0],
        },
        index=pd.to_datetime(["2026-07-10", "2026-06-01"]),
    )

    def get_earnings_dates(self, limit=12):
        return pd.DataFrame(
            {
                "Reported EPS": [3.2],
                "EPS Estimate": [3.0],
            },
            index=pd.to_datetime(["2026-05-15"]),
        )


class StubYahooProvider(YahooProvider):
    def _ticker(self, symbol):
        return FakeTicker()


class YahooStockEventTests(unittest.TestCase):
    def test_normalizes_calendar_earnings_and_actions(self):
        events = StubYahooProvider().get_stock_events(
            "RELIANCE",
            date(2026, 5, 1),
            date(2026, 8, 31),
        )

        event_types = [event.event_type for event in events]
        self.assertIn("Quarterly Results", event_types)
        self.assertIn("Dividend", event_types)
        self.assertIn("Stock Split / Bonus", event_types)

        dividend = next(event for event in events if event.amount == 5.5)
        self.assertEqual(dividend.event_date, date(2026, 7, 10))

        adjustment = next(event for event in events if event.ratio == 2.0)
        self.assertEqual(adjustment.event_date, date(2026, 6, 1))

        past_results = next(
            event
            for event in events
            if event.event_date == date(2026, 5, 15)
        )
        self.assertFalse(past_results.is_estimated)


if __name__ == "__main__":
    unittest.main()

