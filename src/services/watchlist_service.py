from dataclasses import dataclass

from src.models.watchlist_item import WatchlistItem
from src.repositories.price_repository import IPriceRepository
from src.repositories.watchlist_repository import IWatchlistRepository
from src.services.company_service import CompanyService


@dataclass(slots=True)
class WatchlistOverview:
    item: WatchlistItem
    current_price: float | None
    price_date: str | None
    upside_to_target_percent: float | None
    change_from_entry_percent: float | None
    alert_triggered: bool


class WatchlistService:
    VALID_PRIORITIES = {"High", "Medium", "Low"}
    VALID_STATUSES = {"Watching", "Researching", "Ready", "Avoid"}

    def __init__(
        self,
        repository: IWatchlistRepository,
        company_service: CompanyService,
        price_repository: IPriceRepository,
    ):
        self.repository = repository
        self.company_service = company_service
        self.price_repository = price_repository

    def save(
        self,
        symbol: str,
        entry_price: float | None = None,
        target_price: float | None = None,
        alert_price: float | None = None,
        priority: str = "Medium",
        status: str = "Watching",
        thesis: str | None = None,
        notes: str | None = None,
    ) -> WatchlistItem:
        symbol = symbol.strip().upper()
        if not symbol:
            raise ValueError("Symbol is required")
        if priority not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {priority}")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        for label, value in (
            ("Entry price", entry_price),
            ("Target price", target_price),
            ("Alert price", alert_price),
        ):
            if value is not None and value <= 0:
                raise ValueError(f"{label} must be greater than zero")

        company = self.company_service.ensure_company(symbol)
        if company.id is None:
            raise RuntimeError(f"Company id is missing for {symbol}")

        return self.repository.upsert(
            WatchlistItem(
                company_id=company.id,
                symbol=company.symbol,
                company_name=company.company_name,
                entry_price=entry_price,
                target_price=target_price,
                alert_price=alert_price,
                priority=priority,
                status=status,
                thesis=thesis.strip() if thesis else None,
                notes=notes.strip() if notes else None,
            )
        )

    def list_all(self) -> list[WatchlistItem]:
        return self.repository.list_all()

    def get_overview(self) -> list[WatchlistOverview]:
        result = []
        for item in self.repository.list_all():
            prices = self.price_repository.list_by_company(item.company_id)
            latest = prices[-1] if prices else None
            current_price = None
            price_date = None

            if latest is not None:
                current_price = (
                    latest.adjusted_close
                    if latest.adjusted_close is not None
                    else latest.close_price
                )
                price_date = latest.price_date.isoformat()

            upside = None
            if current_price and item.target_price:
                upside = round(
                    (item.target_price / current_price - 1) * 100,
                    2,
                )

            entry_change = None
            if current_price and item.entry_price:
                entry_change = round(
                    (current_price / item.entry_price - 1) * 100,
                    2,
                )

            alert_triggered = bool(
                current_price is not None
                and item.alert_price is not None
                and current_price <= item.alert_price
            )

            result.append(
                WatchlistOverview(
                    item=item,
                    current_price=current_price,
                    price_date=price_date,
                    upside_to_target_percent=upside,
                    change_from_entry_percent=entry_change,
                    alert_triggered=alert_triggered,
                )
            )
        return result

    def remove(self, company_id: int) -> None:
        self.repository.delete(company_id)
