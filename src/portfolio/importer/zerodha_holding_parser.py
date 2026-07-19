from pathlib import Path

import pandas as pd

from src.portfolio.dto.imported_holding import ImportedHolding


class ZerodhaHoldingParser:
    """
    Parses Zerodha Holdings CSV.
    """

    def parse(
        self,
        file_path: str | Path,
    ) -> list[ImportedHolding]:

        df = pd.read_csv(file_path)

        holdings = []

        for _, row in df.iterrows():

            holdings.append(
                ImportedHolding(
                    symbol=str(row["Symbol"]).strip(),
                    isin=str(row["ISIN"]).strip(),
                    quantity=float(row["Quantity Available"]),
                    average_price=float(row["Average Price"]),
                )
            )

        return holdings