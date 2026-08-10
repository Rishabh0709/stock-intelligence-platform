from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING, Protocol

from src.models.stock_event import StockEvent

if TYPE_CHECKING:
    from src.repositories.company_repository import ICompanyRepository
    from src.repositories.portfolio_repository import IPortfolioRepository
    from src.repositories.watchlist_repository import IWatchlistRepository


class StockEventProvider(Protocol):
    def get_stock_events(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[StockEvent]: ...


@dataclass(frozen=True, slots=True)
class TrackedStockEvent:
    company_name: str
    sources: tuple[str, ...]
    event: StockEvent

    @property
    def timing(self) -> str:
        today = date.today()
        if self.event.event_date == today:
            return "Today"
        if self.event.event_date > today:
            return "Upcoming"
        return "Recent"

    @property
    def days_away(self) -> int:
        return (self.event.event_date - date.today()).days


@dataclass(frozen=True, slots=True)
class StockEventFailure:
    symbol: str
    sources: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class StockEventResult:
    events: tuple[TrackedStockEvent, ...]
    failures: tuple[StockEventFailure, ...]
    start_date: date
    end_date: date


class StockEventService:
    """Loads events for the deduplicated Holdings + Watchlist universe."""

    def __init__(
        self,
        company_repository: "ICompanyRepository",
        portfolio_repository: "IPortfolioRepository",
        watchlist_repository: "IWatchlistRepository",
        provider: StockEventProvider,
    ):
        self.company_repository = company_repository
        self.portfolio_repository = portfolio_repository
        self.watchlist_repository = watchlist_repository
        self.provider = provider

    def list_events(
        self,
        *,
        upcoming_days: int = 90,
        recent_days: int = 180,
        include_holdings: bool = True,
        include_watchlist: bool = True,
        as_of: date | None = None,
    ) -> StockEventResult:
        if not include_holdings and not include_watchlist:
            raise ValueError("Select at least one event universe")
        if upcoming_days < 0 or recent_days < 0:
            raise ValueError("Event windows cannot be negative")

        today = as_of or date.today()
        start_date = today - timedelta(days=recent_days)
        end_date = today + timedelta(days=upcoming_days)
        sources_by_company: dict[int, set[str]] = {}

        if include_holdings:
            for holding in self.portfolio_repository.get_all():
                if holding.company_id is not None:
                    sources_by_company.setdefault(holding.company_id, set()).add(
                        "Holding"
                    )

        if include_watchlist:
            for item in self.watchlist_repository.list_all():
                sources_by_company.setdefault(item.company_id, set()).add(
                    "Watchlist"
                )

        events: list[TrackedStockEvent] = []
        failures: list[StockEventFailure] = []

        for company_id, source_set in sources_by_company.items():
            sources = tuple(sorted(source_set))
            company = self.company_repository.get(company_id)
            if company is None:
                failures.append(
                    StockEventFailure(
                        symbol=str(company_id),
                        sources=sources,
                        reason="Company record not found",
                    )
                )
                continue

            try:
                company_events = self.provider.get_stock_events(
                    company.symbol,
                    start_date,
                    end_date,
                )
                for event in company_events:
                    if start_date <= event.event_date <= end_date:
                        events.append(
                            TrackedStockEvent(
                                company_name=company.company_name,
                                sources=sources,
                                event=event,
                            )
                        )
            except Exception as exc:
                failures.append(
                    StockEventFailure(
                        symbol=company.symbol,
                        sources=sources,
                        reason=str(exc) or type(exc).__name__,
                    )
                )

        events.sort(
            key=lambda item: (
                item.event.event_date < today,
                item.event.event_date.toordinal()
                if item.event.event_date >= today
                else -item.event.event_date.toordinal(),
                item.event.symbol,
                item.event.event_type,
            )
        )
        failures.sort(key=lambda item: item.symbol)

        return StockEventResult(
            events=tuple(events),
            failures=tuple(failures),
            start_date=start_date,
            end_date=end_date,
        )
