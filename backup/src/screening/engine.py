from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from src.screening.models import ScanCandidate, StockIntelligenceReport
from src.screening.momentum_engine import momentum_signals
from src.screening.risk_engine import calculate_risk_metrics, find_nearest_resistance
from src.screening.schema import latest_number, normalize_indicator_frame
from src.screening.scoring_engine import calculate_stock_score
from src.screening.trend_engine import trend_signals
from src.screening.volatility_engine import volatility_signals
from src.screening.volume_engine import volume_signals


def analyze_stock(
    df: pd.DataFrame,
    *,
    symbol: str | None = None,
    account_capital: float | None = None,
    risk_percent: float = 1.0,
    resistance: float | None = None,
    highest_price_since_entry: float | None = None,
    minimum_rrr: float = 2.5,
) -> StockIntelligenceReport:
    frame = normalize_indicator_frame(df)
    signals = (
        *trend_signals(frame),
        *momentum_signals(frame),
        *volatility_signals(frame),
        *volume_signals(frame),
    )
    score = calculate_stock_score(frame)
    risk = None
    if account_capital is not None:
        entry = latest_number(frame, "Close")
        atr = latest_number(frame, "ATR_14")
        if entry is None or atr is None:
            raise ValueError("Close and ATR_14 need valid latest values for risk metrics")
        if resistance is None:
            resistance = find_nearest_resistance(frame)
        risk = calculate_risk_metrics(
            entry_price=entry,
            atr=atr,
            account_capital=account_capital,
            risk_percent=risk_percent,
            resistance=resistance,
            highest_price_since_entry=highest_price_since_entry,
            minimum_rrr=minimum_rrr,
        )
    return StockIntelligenceReport(
        symbol=symbol.strip().upper() if symbol else None,
        score=score,
        signals=signals,
        risk=risk,
    )


def scan_stocks(
    frames: Mapping[str, pd.DataFrame],
    *,
    account_capital: float,
    risk_percent: float = 1.0,
    resistance_by_symbol: Mapping[str, float] | None = None,
    minimum_score: int = 60,
    minimum_rrr: float = 2.5,
) -> list[ScanCandidate]:
    """Rank stocks that satisfy both intelligence-score and RRR gates."""
    candidates: list[ScanCandidate] = []
    resistances = resistance_by_symbol or {}
    for raw_symbol, frame in frames.items():
        symbol = raw_symbol.strip().upper()
        report = analyze_stock(
            frame,
            symbol=symbol,
            account_capital=account_capital,
            risk_percent=risk_percent,
            resistance=resistances.get(symbol),
            minimum_rrr=minimum_rrr,
        )
        if report.score.score < minimum_score or not report.risk or not report.risk.eligible:
            continue
        risk = report.risk
        candidates.append(
            ScanCandidate(
                symbol=symbol,
                score=report.score.score,
                category=report.score.category,
                risk_reward_ratio=risk.risk_reward_ratio or 0.0,
                entry_price=risk.entry_price,
                stop_loss=risk.initial_stop,
                resistance=risk.resistance or 0.0,
                quantity=risk.quantity,
                active_signal_keys=tuple(signal.key for signal in report.active_signals),
            )
        )
    return sorted(
        candidates,
        key=lambda candidate: (candidate.score, candidate.risk_reward_ratio),
        reverse=True,
    )
