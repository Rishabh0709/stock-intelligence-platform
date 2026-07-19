from src.portfolio.importer.zerodha_holding_parser import (
    ZerodhaHoldingParser,
)

parser = ZerodhaHoldingParser()

holdings = parser.parse(
    "C:\\Users\\Advik\\Downloads\\holdings_statement.csv",
)

print()

for holding in holdings[:5]:
    print(holding)