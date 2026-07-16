from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class SyncResultDTO:

    company_symbol: str

    downloaded_records: int

    inserted_records: int
    
    skipped_records: int

    latest_price_date: date | None