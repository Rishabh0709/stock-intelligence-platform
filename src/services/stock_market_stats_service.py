from dataclasses import dataclass
from datetime import timedelta

from src.models.daily_price import DailyPrice
from src.providers.data_provider import IDataProvider
from src.repositories.price_repository import IPriceRepository
from src.services.company_service import CompanyService
from src.services.price_sync_service import PriceSyncService


@dataclass(slots=True)
class StockMarketStats:
    symbol: str
    company_id: int
    price_date: str | None
    current_price: float | None
    analysis_price: float | None
    price_1d: float | None
    price_1w: float | None
    price_1m: float | None
    price_6m: float | None
    price_1y: float | None
    price_3y: float | None
    return_1d_percent: float | None
    return_1w_percent: float | None
    return_1m_percent: float | None
    return_6m_percent: float | None
    return_1y_percent: float | None
    return_3y_percent: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None
    overall_high: float | None
    overall_low: float | None


class StockMarketStatsService:
    """Calculates reusable market statistics for any tracked stock."""

    def __init__(
        self,
        company_service: CompanyService,
        price_repository: IPriceRepository,
        price_sync_service: PriceSyncService | None = None,
        provider: IDataProvider | None = None,
    ):
        self.company_service = company_service
        self.price_repository = price_repository
        self.price_sync_service = price_sync_service
        self.provider = provider

    @staticmethod
    def _price_value(price: DailyPrice) -> float:
        return price.analysis_price

    @classmethod
    def _price_on_or_before(
        cls,
        prices: list[DailyPrice],
        target_date,
    ) -> float | None:
        for price in reversed(prices):
            if price.price_date <= target_date:
                return round(cls._price_value(price), 2)
        return None

    @staticmethod
    def _return_percent(
        current_price: float | None,
        historical_price: float | None,
    ) -> float | None:
        if (
            current_price is None
            or historical_price is None
            or historical_price <= 0
        ):
            return None
        return round((current_price / historical_price - 1) * 100, 2)

    @classmethod
    def _historical_values(
        cls,
        prices: list[DailyPrice],
    ) -> dict[str, float | None]:
        empty = {
            "price_1d": None,
            "price_1w": None,
            "price_1m": None,
            "price_6m": None,
            "price_1y": None,
            "price_3y": None,
            "fifty_two_week_high": None,
            "fifty_two_week_low": None,
            "overall_high": None,
            "overall_low": None,
        }
        if not prices:
            return empty

        latest_date = prices[-1].price_date
        lookbacks = {
            "price_1w": 7,
            "price_1m": 30,
            "price_6m": 183,
            "price_1y": 365,
            "price_3y": 1095,
        }
        result = {
            "price_1d": (
                round(cls._price_value(prices[-2]), 2)
                if len(prices) >= 2
                else None
            )
        }
        result.update(
            {
                key: cls._price_on_or_before(
                    prices,
                    latest_date - timedelta(days=days),
                )
                for key, days in lookbacks.items()
            }
        )

        one_year_cutoff = latest_date - timedelta(days=365)
        one_year_values = [
            cls._price_value(price)
            for price in prices
            if price.price_date >= one_year_cutoff
        ]
        all_values = [cls._price_value(price) for price in prices]
        result.update(
            {
                "fifty_two_week_high": (
                    round(max(one_year_values), 2)
                    if one_year_values
                    else None
                ),
                "fifty_two_week_low": (
                    round(min(one_year_values), 2)
                    if one_year_values
                    else None
                ),
                "overall_high": round(max(all_values), 2),
                "overall_low": round(min(all_values), 2),
            }
        )
        return result

    def get_stats(
        self,
        symbol: str,
        *,
        company_id: int | None = None,
        refresh: bool = False,
    ) -> StockMarketStats:
        normalized_symbol = symbol.strip().upper()
        company = self.company_service.get_company(normalized_symbol)
        if company is None:
            company = self.company_service.ensure_company(normalized_symbol)

        resolved_company_id = company_id or company.id
        if resolved_company_id is None:
            raise RuntimeError(f"Company id is missing for {normalized_symbol}")

        if refresh and self.price_sync_service is not None:
            self.price_sync_service.sync(company)

        prices = self.price_repository.list_by_company(resolved_company_id)
        latest = prices[-1] if prices else None
        current_price = (
            round(latest.market_price, 2)
            if latest is not None
            else None
        )
        analysis_price = (
            round(latest.analysis_price, 2)
            if latest is not None
            else None
        )

        snapshot = None
        if refresh and self.provider is not None:
            snapshot = self.provider.get_snapshot(normalized_symbol)
            if snapshot.current_price is not None:
                current_price = round(snapshot.current_price, 2)
                # Live price is already expressed on today's post-corporate-
                # action scale and is comparable with adjusted history.
                analysis_price = current_price

        history = self._historical_values(prices)
        if snapshot is not None:
            if snapshot.fifty_two_week_high is not None:
                history["fifty_two_week_high"] = round(
                    snapshot.fifty_two_week_high,
                    2,
                )
            if snapshot.fifty_two_week_low is not None:
                history["fifty_two_week_low"] = round(
                    snapshot.fifty_two_week_low,
                    2,
                )

        return StockMarketStats(
            symbol=company.symbol,
            company_id=resolved_company_id,
            price_date=(
                latest.price_date.isoformat()
                if latest is not None
                else None
            ),
            current_price=current_price,
            analysis_price=analysis_price,
            **history,
            return_1d_percent=self._return_percent(
                analysis_price,
                history["price_1d"],
            ),
            return_1w_percent=self._return_percent(
                analysis_price,
                history["price_1w"],
            ),
            return_1m_percent=self._return_percent(
                analysis_price,
                history["price_1m"],
            ),
            return_6m_percent=self._return_percent(
                analysis_price,
                history["price_6m"],
            ),
            return_1y_percent=self._return_percent(
                analysis_price,
                history["price_1y"],
            ),
            return_3y_percent=self._return_percent(
                analysis_price,
                history["price_3y"],
            ),
        )
