import sys

from src.cli.commands import CLI


def main():

    cli = CLI()

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