import yfinance as yf

from src.collectors.base_collector import BaseCollector
from src.models.company import Company


class YahooCollector(BaseCollector):

    def get_company(self, symbol: str) -> Company | None:

        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info

            if not info:
                return None

            return Company(
                symbol=symbol,
                company_name=info.get("longName"),
                exchange="NSE",
                isin=info.get("isin"),
                sector=info.get("sector"),
                industry=info.get("industry"),
                country=info.get("country"),
                currency=info.get("currency"),
                website=info.get("website"),
                business_description=info.get("longBusinessSummary"),
            )

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
            
    def get_history(self, symbol, period="5y"):
        ticker = yf.Ticker(f"{symbol}.NS")
        history = ticker.history(period=period)
        return history
        
    def get_snapshot(self, symbol: str):

        ticker = yf.Ticker(f"{symbol}.NS")

        return ticker.info