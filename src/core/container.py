from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.database.db_manager import DatabaseManager
from src.portfolio.portfolio_analyzer import PortfolioAnalyzer
from src.portfolio.portfolio_import_service import PortfolioImportService
from src.providers.data_provider import IDataProvider
from src.recommendation.recommendation_engine import RecommendationEngine
from src.repositories.company_repository import SQLiteCompanyRepository
from src.repositories.portfolio_repository import SQLitePortfolioRepository
from src.repositories.price_repository import SQLitePriceRepository
from src.repositories.watchlist_repository import SQLiteWatchlistRepository
from src.scoring.score_engine import ScoreEngine
from src.services.company_service import CompanyService
from src.services.dashboard_service import DashboardService
from src.services.price_sync_service import PriceSyncService
from src.services.stock_event_service import StockEventService
from src.services.stock_explorer_service import StockExplorerService
from src.services.stock_intelligence_service import StockIntelligenceService
from src.services.stock_market_stats_service import StockMarketStatsService
from src.services.stock_scanner_service import StockScannerService
from src.services.watchlist_analysis_service import WatchlistAnalysisService
from src.services.watchlist_service import WatchlistService


@dataclass(frozen=True, slots=True)
class ContainerValidation:
    missing_dependencies: tuple[str, ...]
    missing_provider_methods: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.missing_dependencies and not self.missing_provider_methods

    def raise_if_invalid(self) -> None:
        if self.is_valid:
            return
        problems = []
        if self.missing_dependencies:
            problems.append(
                "missing dependencies: " + ", ".join(self.missing_dependencies)
            )
        if self.missing_provider_methods:
            problems.append(
                "provider methods: " + ", ".join(self.missing_provider_methods)
            )
        raise RuntimeError("Invalid application container (" + "; ".join(problems) + ")")


class ApplicationContainer:
    """Single composition root for repositories, providers and services.

    Every CLI and Streamlit entry point should obtain dependencies from this
    object. Constructor injection keeps integration tests isolated from the
    production database and live Yahoo calls.
    """

    REQUIRED_DEPENDENCIES = (
        "company_repository",
        "price_repository",
        "portfolio_repository",
        "watchlist_repository",
        "provider",
        "price_sync_service",
        "company_service",
        "portfolio_import_service",
        "portfolio_analyzer",
        "stock_explorer_service",
        "dashboard_service",
        "stock_market_stats_service",
        "watchlist_service",
        "watchlist_analysis_service",
        "stock_intelligence_service",
        "stock_scanner_service",
        "stock_event_service",
    )
    REQUIRED_PROVIDER_METHODS = (
        "get_company",
        "get_snapshot",
        "get_price_history",
        "get_stock_events",
    )

    def __init__(
        self,
        *,
        db_manager: DatabaseManager | None = None,
        provider: IDataProvider | None = None,
    ) -> None:
        self.db_manager = db_manager or DatabaseManager()
        if provider is None:
            # Keep live-provider imports at the composition boundary so unit
            # tests can construct the full service graph without yfinance.
            from src.providers.provider_factory import ProviderFactory

            provider = ProviderFactory.create()
        self.provider = provider

        self.company_repository = SQLiteCompanyRepository(self.db_manager)
        self.price_repository = SQLitePriceRepository(self.db_manager)
        self.portfolio_repository = SQLitePortfolioRepository(self.db_manager)
        self.watchlist_repository = SQLiteWatchlistRepository(self.db_manager)

        self.recommendation_engine = RecommendationEngine()
        self.score_engine = ScoreEngine()

        self.price_sync_service = PriceSyncService(
            provider=self.provider,
            company_repository=self.company_repository,
            price_repository=self.price_repository,
        )
        self.company_service = CompanyService(
            repository=self.company_repository,
            provider=self.provider,
        )
        self.portfolio_import_service = PortfolioImportService(
            company_service=self.company_service,
            portfolio_repository=self.portfolio_repository,
        )
        self.portfolio_analyzer = PortfolioAnalyzer(
            company_repository=self.company_repository,
            portfolio_repository=self.portfolio_repository,
            price_repository=self.price_repository,
            recommendation_engine=self.recommendation_engine,
            score_engine=self.score_engine,
        )
        self.stock_explorer_service = StockExplorerService(
            provider=self.provider,
            company_repository=self.company_repository,
            price_repository=self.price_repository,
            price_sync_service=self.price_sync_service,
        )
        self.dashboard_service = DashboardService(
            company_repository=self.company_repository,
            price_repository=self.price_repository,
            portfolio_analyzer=self.portfolio_analyzer,
        )
        self.stock_market_stats_service = StockMarketStatsService(
            company_service=self.company_service,
            price_repository=self.price_repository,
            price_sync_service=self.price_sync_service,
            provider=self.provider,
        )
        self.watchlist_service = WatchlistService(
            repository=self.watchlist_repository,
            company_service=self.company_service,
            market_stats_service=self.stock_market_stats_service,
        )
        self.watchlist_analysis_service = WatchlistAnalysisService(
            stock_explorer_service=self.stock_explorer_service,
            provider=self.provider,
        )
        self.stock_intelligence_service = StockIntelligenceService(
            company_repository=self.company_repository,
            price_repository=self.price_repository,
            price_sync_service=self.price_sync_service,
        )
        self.stock_scanner_service = StockScannerService(
            company_repository=self.company_repository,
            portfolio_repository=self.portfolio_repository,
            watchlist_repository=self.watchlist_repository,
            intelligence_service=self.stock_intelligence_service,
        )
        self.stock_event_service = StockEventService(
            company_repository=self.company_repository,
            portfolio_repository=self.portfolio_repository,
            watchlist_repository=self.watchlist_repository,
            provider=self.provider,
        )

        self.validate().raise_if_invalid()

    def validate(self) -> ContainerValidation:
        missing_dependencies = tuple(
            name
            for name in self.REQUIRED_DEPENDENCIES
            if getattr(self, name, None) is None
        )
        missing_provider_methods = tuple(
            name
            for name in self.REQUIRED_PROVIDER_METHODS
            if not callable(getattr(self.provider, name, None))
        )
        return ContainerValidation(
            missing_dependencies=missing_dependencies,
            missing_provider_methods=missing_provider_methods,
        )

    def dependency(self, name: str) -> Any:
        """Return a named dependency with a useful integration error."""
        if name not in self.REQUIRED_DEPENDENCIES:
            raise KeyError(f"Unknown application dependency: {name}")
        value = getattr(self, name, None)
        if value is None:
            raise RuntimeError(f"Application dependency is not wired: {name}")
        return value


def create_application(
    *,
    db_manager: DatabaseManager | None = None,
    provider: IDataProvider | None = None,
) -> ApplicationContainer:
    return ApplicationContainer(db_manager=db_manager, provider=provider)
