from dataclasses import dataclass


@dataclass
class DashboardSummary:

    companies: int

    price_records: int

    database_size: float

    portfolio_value: float

    health_score: str