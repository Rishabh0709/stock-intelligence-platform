from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.services.stock_intelligence_service import (
    StockIntelligenceResult,
    StockIntelligenceService,
)

if TYPE_CHECKING:
    from src.repositories.company_repository import ICompanyRepository
    from src.repositories.portfolio_repository import IPortfolioRepository
    from src.repositories.watchlist_repository import IWatchlistRepository


@dataclass(frozen=True, slots=True)
class ScannedStock:
    sources: tuple[str, ...]
    result: StockIntelligenceResult


@dataclass(frozen=True, slots=True)
class ScanFailure:
    symbol: str
    sources: tuple[str, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class StockScanResult:
    stocks: tuple[ScannedStock, ...]
    failures: tuple[ScanFailure, ...]


class StockScannerService:
    """Builds and scans the deduplicated Holdings + Watchlist universe."""

    def __init__(
        self,
        company_repository: "ICompanyRepository",
        portfolio_repository: "IPortfolioRepository",
        watchlist_repository: "IWatchlistRepository",
        intelligence_service: StockIntelligenceService,
    ):
        self.company_repository = company_repository
        self.portfolio_repository = portfolio_repository
        self.watchlist_repository = watchlist_repository
        self.intelligence_service = intelligence_service

    def scan(
        self,
        *,
        account_capital: float,
        risk_percent: float = 1.0,
        minimum_rrr: float = 2.5,
        include_holdings: bool = True,
        include_watchlist: bool = True,
        refresh: bool = False,
    ) -> StockScanResult:
        if not include_holdings and not include_watchlist:
            raise ValueError("Select at least one scanner universe")

        sources_by_company: dict[int, set[str]] = {}
        if include_holdings:
            for holding in self.portfolio_repository.get_all():
                if holding.company_id is not None:
                    sources_by_company.setdefault(holding.company_id, set()).add("Holding")
        if include_watchlist:
            for item in self.watchlist_repository.list_all():
                sources_by_company.setdefault(item.company_id, set()).add("Watchlist")

        stocks: list[ScannedStock] = []
        failures: list[ScanFailure] = []
        for company_id, source_set in sources_by_company.items():
            sources = tuple(sorted(source_set))
            company = self.company_repository.get(company_id)
            symbol = company.symbol if company is not None else str(company_id)
            try:
                result = self.intelligence_service.analyze(
                    company_id,
                    account_capital=account_capital,
                    risk_percent=risk_percent,
                    minimum_rrr=minimum_rrr,
                    refresh=refresh,
                )
                stocks.append(ScannedStock(sources=sources, result=result))
            except Exception as exc:
                failures.append(
                    ScanFailure(symbol=symbol, sources=sources, reason=str(exc))
                )

        stocks.sort(
            key=lambda item: (
                item.result.report.score.score,
                item.result.report.risk.risk_reward_ratio
                if item.result.report.risk
                and item.result.report.risk.risk_reward_ratio is not None
                else -1,
            ),
            reverse=True,
        )
        failures.sort(key=lambda item: item.symbol)
        return StockScanResult(tuple(stocks), tuple(failures))
