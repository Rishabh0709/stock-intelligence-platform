import tempfile
import unittest
from pathlib import Path

from src.portfolio.importer.zerodha_holding_parser import ZerodhaHoldingParser


class ZerodhaHoldingParserTests(unittest.TestCase):
    def test_parses_portable_fixture(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "holdings.csv"
            path.write_text(
                "Symbol,ISIN,Quantity Available,Average Price\n"
                "RELIANCE,INE002A01018,5,1400.50\n",
                encoding="utf-8",
            )
            holdings = ZerodhaHoldingParser().parse(path)

        self.assertEqual(len(holdings), 1)
        self.assertEqual(holdings[0].symbol, "RELIANCE")
        self.assertEqual(holdings[0].quantity, 5)
        self.assertEqual(holdings[0].average_price, 1400.50)


if __name__ == "__main__":
    unittest.main()
