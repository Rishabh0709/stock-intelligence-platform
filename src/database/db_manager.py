from sqlalchemy import create_engine
from config.settings import DATABASE_URL
from src.database.tables import metadata

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        print(f"Using database: {DATABASE_URL}")
        
        # Automatically create tables if they don't exist
        metadata.create_all(self.engine)

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