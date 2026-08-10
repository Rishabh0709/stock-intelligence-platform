from datetime import date, datetime, timedelta, timezone

import pandas as pd
import yfinance as yf

from config.settings import DEFAULT_EXCHANGE
from src.dto.company_dto import CompanyDTO
from src.dto.snapshot_dto import SnapshotDTO
from src.dto.daily_price_dto import DailyPriceDTO
from src.providers.data_provider import IDataProvider
from src.models.stock_event import StockEvent


class YahooProvider(IDataProvider):

    @staticmethod
    def _event_date(value) -> date | None:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None
        if value is None or pd.isna(value):
            return None
        try:
            return pd.Timestamp(value).date()
        except (TypeError, ValueError, OverflowError):
            return None

    @staticmethod
    def _calendar_value(calendar: dict, *names: str):
        normalized = {
            str(key).replace(" ", "").replace("_", "").lower(): value
            for key, value in calendar.items()
        }
        for name in names:
            key = name.replace(" ", "").replace("_", "").lower()
            if key in normalized:
                return normalized[key]
        return None

    def _ticker(self, symbol: str):

        # Yahoo index symbols (for example ^NSEI for Nifty 50) are already
        # fully qualified and must not receive an exchange suffix.
        if symbol.startswith("^"):
            return yf.Ticker(symbol)

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

        history = self._ticker(symbol).history(
            start=start_date,
            # yfinance treats ``end`` as exclusive; the provider contract
            # treats end_date as inclusive.
            end=end_date + timedelta(days=1),
            auto_adjust=False,
        )
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

    def get_stock_events(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[StockEvent]:
        """Return normalized earnings, dividend and split/bonus events."""
        ticker = self._ticker(symbol)
        normalized_symbol = symbol.strip().upper()
        events: list[StockEvent] = []

        try:
            raw_calendar = ticker.calendar or {}
            if isinstance(raw_calendar, pd.DataFrame):
                if len(raw_calendar.columns) == 1:
                    calendar = raw_calendar.iloc[:, 0].to_dict()
                elif len(raw_calendar.index) == 1:
                    calendar = raw_calendar.iloc[0].to_dict()
                else:
                    calendar = {}
            elif isinstance(raw_calendar, pd.Series):
                calendar = raw_calendar.to_dict()
            else:
                calendar = dict(raw_calendar)
        except Exception:
            calendar = {}

        earnings_value = self._calendar_value(
            calendar,
            "Earnings Date",
            "EarningsDate",
        )
        earnings_dates = (
            earnings_value
            if isinstance(earnings_value, (list, tuple))
            else [earnings_value]
        )
        for value in earnings_dates:
            event_date = self._event_date(value)
            if event_date and start_date <= event_date <= end_date:
                events.append(
                    StockEvent(
                        symbol=normalized_symbol,
                        event_date=event_date,
                        event_type="Quarterly Results",
                        title="Quarterly results expected",
                        details=(
                            "Calendar date supplied by Yahoo Finance; verify "
                            "with the exchange/company announcement."
                        ),
                        is_estimated=True,
                    )
                )

        try:
            earnings_history = ticker.get_earnings_dates(limit=12)
        except Exception:
            earnings_history = None

        if (
            isinstance(earnings_history, pd.DataFrame)
            and not earnings_history.empty
        ):
            for timestamp, row in earnings_history.iterrows():
                event_date = self._event_date(timestamp)
                if event_date is None or not start_date <= event_date <= end_date:
                    continue

                reported_eps = pd.to_numeric(
                    row.get("Reported EPS"), errors="coerce"
                )
                estimate_eps = pd.to_numeric(
                    row.get("EPS Estimate"), errors="coerce"
                )
                details = []
                if pd.notna(reported_eps):
                    details.append(f"Reported EPS: {float(reported_eps):g}")
                if pd.notna(estimate_eps):
                    details.append(f"EPS estimate: {float(estimate_eps):g}")

                is_estimated = event_date >= date.today() or pd.isna(reported_eps)
                events.append(
                    StockEvent(
                        symbol=normalized_symbol,
                        event_date=event_date,
                        event_type="Quarterly Results",
                        title=(
                            "Quarterly results expected"
                            if is_estimated
                            else "Quarterly results announced"
                        ),
                        details=(
                            "; ".join(details)
                            or "Quarterly earnings calendar event."
                        ),
                        is_estimated=is_estimated,
                    )
                )

        for key_names, event_type, title in (
            (("Ex-Dividend Date", "ExDividendDate"), "Dividend", "Ex-dividend date"),
            (("Dividend Date", "DividendDate"), "Dividend", "Dividend payment date"),
        ):
            event_date = self._event_date(
                self._calendar_value(calendar, *key_names)
            )
            if event_date and start_date <= event_date <= end_date:
                events.append(
                    StockEvent(
                        symbol=normalized_symbol,
                        event_date=event_date,
                        event_type=event_type,
                        title=title,
                        details="Upcoming dividend calendar event.",
                    )
                )

        try:
            actions = ticker.actions
        except Exception:
            actions = None

        if isinstance(actions, pd.DataFrame) and not actions.empty:
            for timestamp, row in actions.iterrows():
                event_date = self._event_date(timestamp)
                if event_date is None or not start_date <= event_date <= end_date:
                    continue

                dividend = pd.to_numeric(
                    row.get("Dividends"), errors="coerce"
                )
                if pd.notna(dividend) and float(dividend) > 0:
                    events.append(
                        StockEvent(
                            symbol=normalized_symbol,
                            event_date=event_date,
                            event_type="Dividend",
                            title="Dividend",
                            details=f"Dividend of ₹{float(dividend):,.2f} per share.",
                            amount=round(float(dividend), 4),
                        )
                    )

                split = pd.to_numeric(
                    row.get("Stock Splits"), errors="coerce"
                )
                if pd.notna(split) and float(split) > 0:
                    events.append(
                        StockEvent(
                            symbol=normalized_symbol,
                            event_date=event_date,
                            event_type="Stock Split / Bonus",
                            title="Share capital adjustment",
                            details=(
                                f"Yahoo adjustment factor: {float(split):g}. "
                                "Verify whether the corporate action was a "
                                "split or bonus issue."
                            ),
                            ratio=round(float(split), 6),
                        )
                    )

        unique: dict[tuple, StockEvent] = {}
        for event in events:
            key = (
                event.event_date,
                event.event_type,
                event.title,
                event.amount,
                event.ratio,
            )
            unique[key] = event

        return sorted(
            unique.values(),
            key=lambda event: (event.event_date, event.event_type, event.title),
        )
