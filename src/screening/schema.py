from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence

import pandas as pd


OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


_EXACT_ALIASES = {
    "date": "Date",
    "datetime": "Date",
    "timestamp": "Date",
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "adjclose": "Close",
    "adjustedclose": "Close",
    "volume": "Volume",
    "sma20": "SMA_20",
    "sma50": "SMA_50",
    "sma200": "SMA_200",
    "ema20": "EMA_20",
    "ema50": "EMA_50",
    "atr": "ATR_14",
    "atr14": "ATR_14",
    "adx": "ADX_14",
    "adx14": "ADX_14",
    "plusdi": "Plus_DI_14",
    "plusdi14": "Plus_DI_14",
    "dmp": "Plus_DI_14",
    "dmp14": "Plus_DI_14",
    "minusdi": "Minus_DI_14",
    "minusdi14": "Minus_DI_14",
    "dmn": "Minus_DI_14",
    "dmn14": "Minus_DI_14",
    "rsi": "RSI_14",
    "rsi14": "RSI_14",
    "macd": "MACD",
    "macdline": "MACD",
    "macdsignal": "MACD_Signal",
    "signal": "MACD_Signal",
    "macdhist": "MACD_Histogram",
    "macdhistogram": "MACD_Histogram",
    "bbupper": "BB_Upper",
    "bbmiddle": "BB_Middle",
    "bblower": "BB_Lower",
    "obv": "OBV",
    "vwap": "VWAP_Daily",
    "vwapdaily": "VWAP_Daily",
    "vwapweekly": "VWAP_Weekly",
}


def _canonical_column(column: str) -> str | None:
    compact = _compact(column)
    exact = _EXACT_ALIASES.get(compact)
    if exact:
        return exact

    # pandas-ta includes its parameters in names such as MACDh_12_26_9.
    prefix_aliases = (
        ("macdh", "MACD_Histogram"),
        ("macds", "MACD_Signal"),
        ("macd", "MACD"),
        ("bbu", "BB_Upper"),
        ("bbm", "BB_Middle"),
        ("bbl", "BB_Lower"),
        ("dmp", "Plus_DI_14"),
        ("dmn", "Minus_DI_14"),
        ("adx", "ADX_14"),
        ("atr", "ATR_14"),
        ("rsi", "RSI_14"),
    )
    for prefix, canonical in prefix_aliases:
        if compact.startswith(prefix):
            return canonical
    return None


def normalize_indicator_frame(
    df: pd.DataFrame,
    *,
    require_ohlcv: bool = True,
) -> pd.DataFrame:
    """Return a sorted numeric frame with stable scanner column names.

    Common pandas-ta column names are accepted. Existing canonical columns win
    when both a canonical column and one of its aliases are present.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    if df.empty:
        raise ValueError("df must contain at least one row")

    result = df.copy()
    canonical_present = set(result.columns)
    renames: dict[str, str] = {}
    for column in result.columns:
        canonical = _canonical_column(str(column))
        if canonical and canonical not in canonical_present:
            renames[column] = canonical
            canonical_present.add(canonical)
    result = result.rename(columns=renames)

    if "Date" in result.columns:
        result["Date"] = pd.to_datetime(result["Date"], errors="coerce")
        result = result.dropna(subset=["Date"]).sort_values("Date")

    if require_ohlcv:
        require_columns(result, OHLCV_COLUMNS)

    excluded = {"Date", "Symbol"}
    for column in result.columns:
        if column not in excluded:
            result[column] = pd.to_numeric(result[column], errors="coerce")

    return result.reset_index(drop=True)


def build_indicator_frame(
    price_df: pd.DataFrame,
    indicators: Mapping[str, Sequence[float | int | None] | pd.Series],
) -> pd.DataFrame:
    """Attach already-calculated indicator arrays to an OHLCV frame.

    Keys may use canonical names (for example ``SMA_50``) or supported aliases.
    Each indicator must contain exactly one value per price row.
    """
    if not isinstance(price_df, pd.DataFrame):
        raise TypeError("price_df must be a pandas DataFrame")
    result = price_df.copy().reset_index(drop=True)
    for name, values in indicators.items():
        values_list = list(values)
        if len(values_list) != len(result):
            raise ValueError(
                f"Indicator {name!r} has {len(values_list)} values; "
                f"expected {len(result)}"
            )
        result[name] = values_list
    return normalize_indicator_frame(result)


def require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(
            "Missing required indicator columns: " + ", ".join(missing)
        )


def latest_number(df: pd.DataFrame, column: str) -> float | None:
    if column not in df.columns:
        return None
    values = df[column].dropna()
    return float(values.iloc[-1]) if not values.empty else None


def is_close_to(value: float, reference: float, tolerance_pct: float) -> bool:
    if reference == 0:
        return False
    return abs(value - reference) / abs(reference) * 100 <= tolerance_pct


def crossed_above(left: pd.Series, right: pd.Series) -> bool:
    pair = pd.concat([left, right], axis=1).dropna()
    return bool(
        len(pair) >= 2
        and pair.iloc[-2, 0] <= pair.iloc[-2, 1]
        and pair.iloc[-1, 0] > pair.iloc[-1, 1]
    )


def crossed_below(left: pd.Series, right: pd.Series) -> bool:
    pair = pd.concat([left, right], axis=1).dropna()
    return bool(
        len(pair) >= 2
        and pair.iloc[-2, 0] >= pair.iloc[-2, 1]
        and pair.iloc[-1, 0] < pair.iloc[-1, 1]
    )
