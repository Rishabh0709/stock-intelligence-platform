from datetime import date, timedelta

from src.analytics.core.price_series import PriceSeries
from src.models.company import Company
from src.models.daily_price import DailyPrice
from src.models.stock_data import StockData


def make_prices(count: int = 3, *, start: float = 100.0) -> list[DailyPrice]:
    base = date(2025, 1, 1)
    return [
        DailyPrice(
            company_id=1,
            price_date=base + timedelta(days=index),
            open_price=start + index - 1,
            high_price=start + index + 2,
            low_price=start + index - 2,
            close_price=start + index,
            adjusted_close=start + index,
            volume=1000 + index,
        )
        for index in range(count)
    ]


def make_series(count: int = 3, *, start: float = 100.0) -> PriceSeries:
    return PriceSeries(make_prices(count, start=start))


def make_stock(count: int = 3) -> StockData:
    return StockData(
        company=Company(id=1, symbol="RELIANCE", company_name="Reliance Industries"),
        price_series=make_series(count),
    )
