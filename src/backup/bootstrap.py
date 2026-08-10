from src.providers.yahoo_provider import YahooProvider
from src.repositories.company_repository import SQLiteCompanyRepository
from src.repositories.price_repository import SQLitePriceRepository
from src.repositories.portfolio_repository import SQLitePortfolioRepository
from src.services.price_sync_service import PriceSyncService
from src.services.company_service import CompanyService
from src.database.db_manager import DatabaseManager
from src.services.stock_explorer_service import StockExplorerService
from src.portfolio.portfolio_import_service import PortfolioImportService
from src.portfolio.portfolio_analyzer import PortfolioAnalyzer
from src.recommendation.recommendation_engine import RecommendationEngine
from src.scoring.score_engine import ScoreEngine
from src.services.dashboard_service import DashboardService
from src.repositories.watchlist_repository import SQLiteWatchlistRepository
from src.services.watchlist_service import WatchlistService
from src.services.watchlist_analysis_service import WatchlistAnalysisService
from src.services.stock_market_stats_service import StockMarketStatsService


class Bootstrap:

    def __init__(self):
        db = DatabaseManager()

        self.company_repository = SQLiteCompanyRepository(db)
        self.price_repository = SQLitePriceRepository(db)
        self.portfolio_repository = SQLitePortfolioRepository(db)
        self.watchlist_repository = SQLiteWatchlistRepository(db)
        self.recommendation_engine = RecommendationEngine()
        self.score_engine = ScoreEngine()
        self.provider = YahooProvider()
        self.price_sync_service = PriceSyncService(
        provider=self.provider,
        company_repository=self.company_repository,
        price_repository=self.price_repository,
        )

        self.company_service = CompanyService(
                               repository = self.company_repository,
                               provider = self.provider
                               )
        self.portfolio_import_service = PortfolioImportService(
                                        company_service=self.company_service,
                                        portfolio_repository=self.portfolio_repository
                                        )
        self.portfolio_analyzer = PortfolioAnalyzer(
                                        company_repository = self.company_repository,
                                        portfolio_repository = self.portfolio_repository,
                                        price_repository = self.price_repository,
                                        recommendation_engine = self.recommendation_engine,
                                        score_engine = self.score_engine
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
