import math
from dataclasses import dataclass
from datetime import timedelta
from statistics import stdev

from src.models.daily_price import DailyPrice
from src.services.stock_explorer_service import StockExplorerService


@dataclass(slots=True)
class WatchlistStockReview:
    symbol: str
    company_name: str
    sector: str | None
    industry: str | None
    price_as_of: str
    current_price: float
    price: dict
    returns_percent: dict
    risk: dict
    technical: dict
    valuation: dict
    signals: list[str]
    price_history: list[dict]


class WatchlistAnalysisService:
    """Builds a deterministic stock review without using an LLM."""

    def __init__(
        self,
        stock_explorer_service: StockExplorerService,
        provider,
    ):
        self.stock_explorer_service = stock_explorer_service
        self.provider = provider

    @staticmethod
    def _price_value(price: DailyPrice) -> float:
        return (
            price.adjusted_close
            if price.adjusted_close is not None
            else price.close_price
        )

    @classmethod
    def _return_for_days(
        cls,
        prices: list[DailyPrice],
        days: int,
    ) -> float | None:
        if len(prices) < 2:
            return None

        cutoff = prices[-1].price_date - timedelta(days=days)
        candidates = [price for price in prices if price.price_date <= cutoff]
        if not candidates:
            return None

        start = cls._price_value(candidates[-1])
        end = cls._price_value(prices[-1])
        if start <= 0:
            return None
        return round((end / start - 1) * 100, 2)

    @classmethod
    def _annualized_volatility(
        cls,
        prices: list[DailyPrice],
    ) -> float | None:
        values = [cls._price_value(price) for price in prices[-253:]]
        log_returns = [
            math.log(current / previous)
            for previous, current in zip(values, values[1:])
            if previous > 0 and current > 0
        ]
        if len(log_returns) < 2:
            return None
        return round(stdev(log_returns) * math.sqrt(252) * 100, 2)

    @classmethod
    def _max_drawdown(
        cls,
        prices: list[DailyPrice],
    ) -> float | None:
        values = [cls._price_value(price) for price in prices[-253:]]
        if not values:
            return None

        peak = values[0]
        worst = 0.0
        for value in values:
            peak = max(peak, value)
            if peak > 0:
                worst = min(worst, (value / peak - 1) * 100)
        return round(worst, 2)

    @classmethod
    def _moving_average(
        cls,
        prices: list[DailyPrice],
        window: int,
    ) -> float | None:
        if len(prices) < window:
            return None
        values = [cls._price_value(price) for price in prices[-window:]]
        return round(sum(values) / window, 2)

    @staticmethod
    def _build_signals(
        current_price: float,
        ma_50: float | None,
        ma_200: float | None,
        entry_price: float | None,
        target_price: float | None,
        alert_price: float | None,
    ) -> list[str]:
        signals = []

        if ma_50 is not None:
            direction = "above" if current_price >= ma_50 else "below"
            signals.append(f"Price is {direction} the 50-day moving average.")

        if ma_200 is not None:
            direction = "above" if current_price >= ma_200 else "below"
            signals.append(f"Price is {direction} the 200-day moving average.")

        if ma_50 is not None and ma_200 is not None:
            structure = "positive" if ma_50 >= ma_200 else "weak"
            signals.append(
                f"Medium-term trend structure is {structure} "
                f"(50-DMA {'≥' if ma_50 >= ma_200 else '<'} 200-DMA)."
            )

        if entry_price is not None:
            change = (current_price / entry_price - 1) * 100
            signals.append(
                f"Price is {abs(change):.2f}% "
                f"{'above' if change >= 0 else 'below'} the reference price."
            )

        if target_price is not None:
            if current_price >= target_price:
                signals.append("The saved target price has been reached.")
            else:
                upside = (target_price / current_price - 1) * 100
                signals.append(f"Saved target is {upside:.2f}% above the price.")

        if alert_price is not None and current_price <= alert_price:
            signals.append("Price is at or below the saved alert level.")

        return signals

    def analyze(
        self,
        symbol: str,
        *,
        entry_price: float | None = None,
        target_price: float | None = None,
        alert_price: float | None = None,
    ) -> WatchlistStockReview:
        stock = self.stock_explorer_service.get_stock(symbol)
        prices = stock.price_series.prices
        if not prices:
            raise ValueError(f"No prices available for {symbol}")

        snapshot = self.provider.get_snapshot(symbol)
        latest = prices[-1]
        latest_adjusted_close = self._price_value(latest)
        current_price = snapshot.current_price or latest_adjusted_close
        one_year_prices = prices[-253:]
        one_year_values = [
            self._price_value(price) for price in one_year_prices
        ]
        ma_50 = self._moving_average(prices, 50)
        ma_200 = self._moving_average(prices, 200)

        latest_volumes = [
            price.volume for price in prices[-20:] if price.volume is not None
        ]
        average_volume = (
            round(sum(latest_volumes) / len(latest_volumes))
            if latest_volumes
            else None
        )

        return WatchlistStockReview(
            symbol=stock.company.symbol,
            company_name=stock.company.company_name,
            sector=stock.company.sector,
            industry=stock.company.industry,
            price_as_of=latest.price_date.isoformat(),
            current_price=round(current_price, 2),
            price={
                "latest_adjusted_close": round(latest_adjusted_close, 2),
                "previous_close": snapshot.previous_close,
                "52_week_high": round(max(one_year_values), 2),
                "52_week_low": round(min(one_year_values), 2),
                "latest_volume": latest.volume,
                "20_day_average_volume": average_volume,
            },
            returns_percent={
                "1_month": self._return_for_days(prices, 30),
                "3_month": self._return_for_days(prices, 90),
                "6_month": self._return_for_days(prices, 180),
                "1_year": self._return_for_days(prices, 365),
            },
            risk={
                "annualized_volatility_1y":
                    self._annualized_volatility(prices),
                "maximum_drawdown_1y": self._max_drawdown(prices),
            },
            technical={
                "50_day_moving_average": ma_50,
                "200_day_moving_average": ma_200,
            },
            valuation={
                "market_cap": snapshot.market_cap,
                "trailing_pe": snapshot.trailing_pe,
                "forward_pe": snapshot.forward_pe,
                "price_to_book": snapshot.price_to_book,
                "peg_ratio": snapshot.peg_ratio,
                "dividend_yield": snapshot.dividend_yield,
            },
            signals=self._build_signals(
                current_price=current_price,
                ma_50=ma_50,
                ma_200=ma_200,
                entry_price=entry_price,
                target_price=target_price,
                alert_price=alert_price,
            ),
            price_history=[
                {
                    "Date": price.price_date,
                    "Adjusted Close": self._price_value(price),
                }
                for price in one_year_prices
            ],
        )
