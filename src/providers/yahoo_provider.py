from datetime import date

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