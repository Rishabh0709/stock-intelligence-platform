import argparse
from src.bootstrap import Bootstrap
from src.cli.commands import CLI

def main():

    parser = argparse.ArgumentParser(
        description="Stock Intelligence Platform"
    )

    subparsers = parser.add_subparsers(dest="command")

    sync_parser = subparsers.add_parser(
        "sync",
        help="Synchronize stock prices",
    )

    sync_parser.add_argument(
        "symbol",
        help="Stock Symbol",
    )
    bootstrap = Bootstrap()

    company = bootstrap.company_repository.get_by_symbol("RELIANCE")

    rows = bootstrap.price_repository.list_by_company(company.id)

    print(rows[0])
    args = parser.parse_args()

    cli = CLI()

    if args.command == "sync":
        cli.sync(args.symbol.upper())

    else:
        parser.print_help()


if __name__ == "__main__":
    main()