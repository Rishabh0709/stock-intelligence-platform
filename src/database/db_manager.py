from sqlalchemy import create_engine, event

from config.settings import DATABASE_URL
from src.database.tables import metadata

class DatabaseManager:
    def __init__(
        self,
        database_url: str | None = None,
        *,
        create_schema: bool = True,
        echo: bool = False,
    ):
        """Own the SQLAlchemy engine used by the application.

        ``database_url`` is injectable so integration tests can use a temporary
        database without touching the user's real portfolio database.
        """
        self.database_url = database_url or DATABASE_URL
        self.engine = create_engine(self.database_url, echo=echo)

        @event.listens_for(self.engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        if create_schema:
            from src.database.migrations import upgrade_database

            upgrade_database(self.database_url)

    def test_connection(self):
        
        try:
            with self.engine.connect():
                return True, None
                
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False, str(e)
        

    
        
    def recreate_database(self):
        metadata.drop_all(self.engine)
        metadata.create_all(self.engine)
