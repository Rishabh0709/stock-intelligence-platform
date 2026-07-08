import sys

from src.database.db_manager import DatabaseManager
from src.cli.commands import CLI


def main():

    cli = CLI()
    db = DatabaseManager()
    db.recreate_database()
    from sqlalchemy import inspect

    db = DatabaseManager()

    inspector = inspect(db.engine)

    print(inspector.get_table_names())

    if len(sys.argv) < 2:
        print(
            """
Usage:

python main.py import RELIANCE

python main.py list

python main.py search RELIANCE
"""
        )
        return

    command = sys.argv[1]

    if command == "import":

        cli.import_company(sys.argv[2])

    elif command == "list":

        cli.list_companies()

    elif command == "search":

        cli.search_company(sys.argv[2])

    else:

        print("Unknown command")

    
    
if __name__ == "__main__":
    main()