from src.collectors.yahoo_collector import YahooCollector
from src.models.stock_snapshot import StockSnapshot


class StockExplorerService:

    def __init__(self, collector: YahooCollector):

        self.collector = collector

    def get_snapshot(self, symbol: str) -> StockSnapshot:

        info = self.collector.get_snapshot(symbol)

        snapshot = StockSnapshot(

            symbol=info.get("symbol"),

            company_name=info.get("longName"),

            exchange=info.get("exchange"),

            sector=info.get("sector"),

            industry=info.get("industry"),

            website=info.get("website"),

            business_summary=info.get("longBusinessSummary"),

            country=info.get("country"),

            currency=info.get("currency"),

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

            roe=info.get("returnOnEquity"),

            roa=info.get("returnOnAssets"),

            gross_margin=info.get("grossMargins"),

            operating_margin=info.get("operatingMargins"),

            profit_margin=info.get("profitMargins"),

            revenue_growth=info.get("revenueGrowth"),

            earnings_growth=info.get("earningsGrowth"),

            dividend_rate=info.get("dividendRate"),

            dividend_yield=info.get("dividendYield"),

            payout_ratio=info.get("payoutRatio"),

            ex_dividend_date=info.get("exDividendDate")
        )

        return snapshot