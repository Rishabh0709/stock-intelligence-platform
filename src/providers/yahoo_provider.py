from datetime import date, datetime, timezone

import pandas as pd
import yfinance as yf

from config.settings import DEFAULT_EXCHANGE
from src.dto.company_dto import CompanyDTO
from src.dto.snapshot_dto import SnapshotDTO
from src.dto.daily_price_dto import DailyPriceDTO
from src.providers.data_provider import IDataProvider


class YahooProvider(IDataProvider):

    def _ticker(self, symbol: str):

        exchange_suffix = ".NS"

        if DEFAULT_EXCHANGE == "BSE":
            exchange_suffix = ".BO"

        return yf.Ticker(f"{symbol}{exchange_suffix}")

    def get_company(
        self,
        symbol: str
    ) -> CompanyDTO:

        info = self._ticker(symbol).info

        return CompanyDTO(

            symbol=symbol.upper(),

            company_name=info.get("longName", symbol),

            exchange=info.get("exchange", DEFAULT_EXCHANGE),

            isin=info.get("isin"),

            sector=info.get("sector"),

            industry=info.get("industry"),

            country=info.get("country"),

            currency=info.get("currency"),

            website=info.get("website"),

            business_description=info.get("longBusinessSummary"),
        )

    def get_snapshot(
        self,
        symbol: str
    ) -> SnapshotDTO:

        info = self._ticker(symbol).info

        return SnapshotDTO(

            symbol=symbol,

            current_price=info.get("currentPrice"),

            previous_close=info.get("previousClose"),

            open_price=info.get("open"),

            day_high=info.get("dayHigh"),

            day_low=info.get("dayLow"),

            fifty_two_week_high=info.get("fiftyTwoWeekHigh"),

            fifty_two_week_low=info.get("fiftyTwoWeekLow"),

            volume=info.get("volume"),

            average_volume=info.get("averageVolume"),

            market_cap=info.get("marketCap"),

            enterprise_value=info.get("enterpriseValue"),

            shares_outstanding=info.get("sharesOutstanding"),

            trailing_pe=info.get("trailingPE"),

            forward_pe=info.get("forwardPE"),

            price_to_book=info.get("priceToBook"),

            peg_ratio=info.get("pegRatio"),

            dividend_yield=info.get("dividendYield"),
        )

    def get_price_history(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        ) -> list[DailyPriceDTO]:

        history = self._ticker(symbol).history(start=start_date, end=end_date, auto_adjust=False,)
        history = history.dropna(
            subset=[
            "Open",
            "High",
            "Low",
            "Close",
            ]
            )
        prices = []

        for price_date, row in history.iterrows():

            prices.append(

                DailyPriceDTO(
                price_date=price_date.date(),
                open_price=float(row["Open"]),
                high_price=float(row["High"]),
                low_price=float(row["Low"]),
                close_price=float(row["Close"]),
                adjusted_close = (None if pd.isna(row["Adj Close"]) else float(row["Adj Close"])),
                volume=int(row["Volume"])
                )
            )

        return prices

    def get_recent_news(
        self,
        symbol: str,
        limit: int = 8,
    ) -> list[dict]:
        """
        Returns a normalized subset of recent Yahoo Finance news.

        Yahoo's response shape has changed over time, so this method accepts
        both the legacy flat payload and the newer nested ``content`` payload.
        """
        raw_items = self._ticker(symbol).news or []
        normalized = []

        for raw in raw_items[:limit]:
            content = raw.get("content") or raw
            canonical = content.get("canonicalUrl") or {}
            click_through = content.get("clickThroughUrl") or {}
            provider = content.get("provider") or {}

            timestamp = (
                content.get("pubDate")
                or content.get("displayTime")
                or raw.get("providerPublishTime")
            )

            if isinstance(timestamp, (int, float)):
                timestamp = datetime.fromtimestamp(
                    timestamp,
                    tz=timezone.utc,
                ).isoformat()

            url = (
                canonical.get("url")
                or click_through.get("url")
                or content.get("link")
                or raw.get("link")
            )

            title = content.get("title") or raw.get("title")
            if not title:
                continue

            normalized.append(
                {
                    "title": title,
                    "publisher": (
                        provider.get("displayName")
                        or content.get("publisher")
                        or raw.get("publisher")
                    ),
                    "published_at": timestamp,
                    "url": url,
                    "summary": (
                        content.get("summary")
                        or content.get("description")
                    ),
                }
            )

        return normalized
