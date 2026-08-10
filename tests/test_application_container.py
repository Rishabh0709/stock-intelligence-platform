import tempfile
import unittest
from datetime import date
from pathlib import Path
from src.bootstrap import Bootstrap
from src.core.container import ApplicationContainer, create_application
from src.database.db_manager import DatabaseManager


class ProviderStub:
    def get_company(self, symbol):
        raise AssertionError("Live provider access is not expected in this test")

    def get_snapshot(self, symbol):
        raise AssertionError("Live provider access is not expected in this test")

    def get_price_history(self, symbol, start_date, end_date):
        return []

    def get_stock_events(self, symbol, start_date, end_date):
        return []


class ApplicationContainerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "smoke.db"
        self.db = DatabaseManager(f"sqlite:///{database_path}")

    def tearDown(self):
        self.db.engine.dispose()
        self.temp_dir.cleanup()

    def test_complete_service_graph_is_wired(self):
        app = create_application(db_manager=self.db, provider=ProviderStub())

        validation = app.validate()
        self.assertTrue(validation.is_valid)
        self.assertIs(
            app.stock_scanner_service.intelligence_service,
            app.stock_intelligence_service,
        )
        self.assertIs(app.stock_event_service.provider, app.provider)

    def test_bootstrap_remains_compatible(self):
        app = Bootstrap(db_manager=self.db, provider=ProviderStub())

        self.assertIsInstance(app, ApplicationContainer)
        self.assertIsNotNone(app.stock_scanner_service)
        self.assertIsNotNone(app.stock_event_service)


if __name__ == "__main__":
    unittest.main()
