from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class RiskAnalysis:

    date: date

    cagr: float | None

    annual_volatility: float | None

    current_drawdown: float | None

    maximum_drawdown: float | None

    atr: float | None

    risk_level: str

    drawdown_level: str

    volatility_level: str