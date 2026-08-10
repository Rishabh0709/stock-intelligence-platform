from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from src.screening import StockIntelligenceReport, analyze_stock

if TYPE_CHECKING:
    from src.repositories.company_repository import ICompanyRepository
    from src.repositories.price_repository import IPriceRepository
    from src.services.price_sync_service import PriceSyncService


@dataclass(frozen=True, slots=True)
class StockIntelligenceResult:
    symbol: str
    company_name: str
    sector: str | None
    price_as_of: date
    history_rows: int
    is_stale: bool
    report: StockIntelligenceReport
    indicator_frame: pd.DataFrame


class StockIntelligenceService:
    """Prepares stored OHLCV data and runs the deterministic signal engine."""

    def __init__(
        self,
        company_repository: "ICompanyRepository",
        price_repository: "IPriceRepository",
        price_sync_service: "PriceSyncService | None" = None,
        stale_after_days: int = 5,
        minimum_history_rows: int = 35,
    ):
        self.company_repository = company_repository
        self.price_repository = price_repository
        self.price_sync_service = price_sync_service
        self.stale_after_days = stale_after_days
        self.minimum_history_rows = minimum_history_rows

    def analyze(
        self,
        company_id: int,
        *,
        account_capital: float,
        risk_percent: float = 1.0,
        minimum_rrr: float = 2.5,
        refresh: bool = False,
    ) -> StockIntelligenceResult:
        company = self.company_repository.get(company_id)
        if company is None:
            raise ValueError(f"Company {company_id} was not found")

        if refresh and self.price_sync_service is not None:
            self.price_sync_service.sync(company)

        prices = self.price_repository.list_by_company(company_id)
        if len(prices) < self.minimum_history_rows:
            raise ValueError(
                f"{company.symbol} has {len(prices)} price rows; "
                f"at least {self.minimum_history_rows} are required"
            )

        frame = self._build_indicator_frame(prices)
        report = analyze_stock(
            frame,
            symbol=company.symbol,
            account_capital=account_capital,
            risk_percent=risk_percent,
            minimum_rrr=minimum_rrr,
        )
        price_as_of = prices[-1].price_date
        return StockIntelligenceResult(
            symbol=company.symbol,
            company_name=company.company_name,
            sector=company.sector,
            price_as_of=price_as_of,
            history_rows=len(prices),
            is_stale=price_as_of < date.today() - timedelta(days=self.stale_after_days),
            report=report,
            indicator_frame=frame,
        )

    @staticmethod
    def _build_indicator_frame(prices) -> pd.DataFrame:
        frame = pd.DataFrame(
            {
                "Date": [price.price_date for price in prices],
                "Open": [price.open_price for price in prices],
                "High": [price.high_price for price in prices],
                "Low": [price.low_price for price in prices],
                "Close": [price.close_price for price in prices],
                "Volume": [price.volume for price in prices],
            }
        ).sort_values("Date").reset_index(drop=True)

        for column in ("Open", "High", "Low", "Close", "Volume"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

        close = frame["Close"]
        high = frame["High"]
        low = frame["Low"]
        volume = frame["Volume"].fillna(0.0)

        frame["SMA_20"] = close.rolling(20, min_periods=20).mean()
        frame["SMA_50"] = close.rolling(50, min_periods=50).mean()
        frame["SMA_200"] = close.rolling(200, min_periods=200).mean()
        frame["EMA_20"] = close.ewm(span=20, adjust=False, min_periods=20).mean()
        frame["EMA_50"] = close.ewm(span=50, adjust=False, min_periods=50).mean()

        previous_close = close.shift(1)
        true_range = pd.concat(
            [
                high - low,
                (high - previous_close).abs(),
                (low - previous_close).abs(),
            ],
            axis=1,
        ).max(axis=1)
        frame["ATR_14"] = true_range.ewm(
            alpha=1 / 14,
            adjust=False,
            min_periods=14,
        ).mean()

        delta = close.diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)
        average_gain = gains.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
        average_loss = losses.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
        relative_strength = average_gain / average_loss.replace(0, np.nan)
        frame["RSI_14"] = 100 - (100 / (1 + relative_strength))
        frame.loc[(average_loss == 0) & (average_gain > 0), "RSI_14"] = 100.0

        ema12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
        ema26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
        frame["MACD"] = ema12 - ema26
        frame["MACD_Signal"] = frame["MACD"].ewm(
            span=9,
            adjust=False,
            min_periods=9,
        ).mean()
        frame["MACD_Histogram"] = frame["MACD"] - frame["MACD_Signal"]

        frame["BB_Middle"] = frame["SMA_20"]
        rolling_std = close.rolling(20, min_periods=20).std(ddof=0)
        frame["BB_Upper"] = frame["BB_Middle"] + 2 * rolling_std
        frame["BB_Lower"] = frame["BB_Middle"] - 2 * rolling_std

        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = pd.Series(
            np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
            index=frame.index,
        )
        minus_dm = pd.Series(
            np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
            index=frame.index,
        )
        atr = frame["ATR_14"].replace(0, np.nan)
        frame["Plus_DI_14"] = 100 * plus_dm.ewm(
            alpha=1 / 14, adjust=False, min_periods=14
        ).mean() / atr
        frame["Minus_DI_14"] = 100 * minus_dm.ewm(
            alpha=1 / 14, adjust=False, min_periods=14
        ).mean() / atr
        di_sum = frame["Plus_DI_14"] + frame["Minus_DI_14"]
        dx = 100 * (
            (frame["Plus_DI_14"] - frame["Minus_DI_14"]).abs()
            / di_sum.replace(0, np.nan)
        )
        frame["ADX_14"] = dx.ewm(
            alpha=1 / 14, adjust=False, min_periods=14
        ).mean()

        direction = np.sign(close.diff()).fillna(0.0)
        frame["OBV"] = (direction * volume).cumsum()
        typical_price = (high + low + close) / 3
        price_volume = typical_price * volume
        # End-of-day candles cannot provide intraday VWAP. These are stable
        # 5-session and 20-session rolling volume-weighted price proxies.
        frame["VWAP_Daily"] = (
            price_volume.rolling(5, min_periods=1).sum()
            / volume.rolling(5, min_periods=1).sum().replace(0, np.nan)
        )
        frame["VWAP_Weekly"] = (
            price_volume.rolling(20, min_periods=1).sum()
            / volume.rolling(20, min_periods=1).sum().replace(0, np.nan)
        )
        return frame
