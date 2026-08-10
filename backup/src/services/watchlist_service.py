from dataclasses import dataclass

from src.models.watchlist_item import WatchlistItem
from src.repositories.watchlist_repository import IWatchlistRepository
from src.services.company_service import CompanyService
from src.services.stock_market_stats_service import StockMarketStatsService


@dataclass(slots=True)
class WatchlistOverview:
    item: WatchlistItem
    current_price: float | None
    price_date: str | None
    price_1d: float | None
    price_1w: float | None
    price_1m: float | None
    price_6m: float | None
    price_1y: float | None
    price_3y: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None
    overall_high: float | None
    overall_low: float | None
    upside_to_target_percent: float | None
    alert_triggered: bool


class WatchlistService:
    def __init__(
        self,
        repository: IWatchlistRepository,
        company_service: CompanyService,
        market_stats_service: StockMarketStatsService,
    ):
        self.repository = repository
        self.company_service = company_service
        self.market_stats_service = market_stats_service

    def save(
        self,
        symbol: str,
        target_price: float | None = None,
        alert_price: float | None = None,
    ) -> WatchlistItem:
        symbol = symbol.strip().upper()

        if not symbol:
            raise ValueError("Symbol is required")

        if target_price is None:
            raise ValueError("Target price is required")

        if alert_price is None:
            raise ValueError("Alert price is required")

        for label, value in (
            ("Target price", target_price),
            ("Alert price", alert_price),
        ):
            if value <= 0:
                raise ValueError(f"{label} must be greater than zero")

        company = self.company_service.ensure_company(symbol)

        if company.id is None:
            raise RuntimeError(f"Company id is missing for {symbol}")

        return self.repository.upsert(
            WatchlistItem(
                company_id=company.id,
                symbol=company.symbol,
                company_name=company.company_name,
                target_price=target_price,
                alert_price=alert_price,
            )
        )

    def list_all(self) -> list[WatchlistItem]:
        return self.repository.list_all()

    def get_overview(
        self,
        *,
        refresh: bool = False,
    ) -> list[WatchlistOverview]:
        overview_rows = []

        for item in self.repository.list_all():
            stats = self.market_stats_service.get_stats(
                item.symbol,
                company_id=item.company_id,
                refresh=refresh,
            )

            upside = None

            if stats.current_price and item.target_price:
                upside = round(
                    (item.target_price / stats.current_price - 1) * 100,
                    2,
                )

            alert_triggered = bool(
                stats.current_price is not None
                and item.alert_price is not None
                and stats.current_price <= item.alert_price
            )

            overview_rows.append(
                WatchlistOverview(
                    item=item,
                    current_price=stats.current_price,
                    price_date=stats.price_date,
                    price_1d=stats.price_1d,
                    price_1w=stats.price_1w,
                    price_1m=stats.price_1m,
                    price_6m=stats.price_6m,
                    price_1y=stats.price_1y,
                    price_3y=stats.price_3y,
                    fifty_two_week_high=stats.fifty_two_week_high,
                    fifty_two_week_low=stats.fifty_two_week_low,
                    overall_high=stats.overall_high,
                    overall_low=stats.overall_low,
                    upside_to_target_percent=upside,
                    alert_triggered=alert_triggered,
                )
            )

        return overview_rows

    def remove(self, company_id: int) -> None:
        self.repository.delete(company_id)