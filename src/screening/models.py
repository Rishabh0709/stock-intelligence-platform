from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Signal:
    key: str
    name: str
    active: bool
    direction: str
    explanation: str
    values: dict[str, float | int | str | bool | None] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScoreComponent:
    key: str
    label: str
    points: int
    max_points: int
    passed: bool
    explanation: str


@dataclass(frozen=True, slots=True)
class IntelligenceScore:
    score: int
    category: str
    components: tuple[ScoreComponent, ...]

    @property
    def max_score(self) -> int:
        return sum(component.max_points for component in self.components)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RiskMetrics:
    entry_price: float
    atr: float
    initial_stop: float
    trailing_stop: float
    resistance: float | None
    reward_per_share: float | None
    risk_per_share: float
    risk_reward_ratio: float | None
    account_risk_amount: float
    quantity: int
    position_value: float
    eligible: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StockIntelligenceReport:
    symbol: str | None
    score: IntelligenceScore
    signals: tuple[Signal, ...]
    risk: RiskMetrics | None = None

    @property
    def active_signals(self) -> tuple[Signal, ...]:
        return tuple(signal for signal in self.signals if signal.active)

    def to_dict(self) -> dict[str, Any]:
        return {
            "symbol": self.symbol,
            "score": self.score.to_dict(),
            "signals": [signal.to_dict() for signal in self.signals],
            "risk": self.risk.to_dict() if self.risk else None,
        }


@dataclass(frozen=True, slots=True)
class ScanCandidate:
    symbol: str
    score: int
    category: str
    risk_reward_ratio: float
    entry_price: float
    stop_loss: float
    resistance: float
    quantity: int
    active_signal_keys: tuple[str, ...]

