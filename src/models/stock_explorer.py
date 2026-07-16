@dataclass
class StockExplorer:

    company: Company

    snapshot: StockSnapshot

    price_history: list[DailyPrice]

    recommendation: Recommendation | None

    financials: Financials | None