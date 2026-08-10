"""
Shared constants used across the analytics package.

This module contains:

- Time-related constants
- Financial defaults
- Indicator default parameters
- Trading signal labels
- Trend interpretation labels

These constants are intentionally centralized so that
all calculators use the same defaults and terminology.
"""

# ==========================================================
# Time
# ==========================================================

TRADING_DAYS_PER_YEAR = 252

CALENDAR_DAYS_PER_YEAR = 365.25

MONTHS_PER_YEAR = 12

WEEKS_PER_YEAR = 52


# ==========================================================
# Financial Defaults
# ==========================================================

# Default annual risk-free rate.
# Can later be replaced with dynamically fetched
# government bond or treasury bill yields.
DEFAULT_RISK_FREE_RATE = 0.06


# ==========================================================
# Moving Averages
# ==========================================================

DEFAULT_SMA_WINDOW = 20

DEFAULT_EMA_WINDOW = 20


# ==========================================================
# Relative Strength Index (RSI)
# ==========================================================

DEFAULT_RSI_PERIOD = 14


# ==========================================================
# Moving Average Convergence Divergence (MACD)
# ==========================================================

DEFAULT_MACD_FAST = 12

DEFAULT_MACD_SLOW = 26

DEFAULT_MACD_SIGNAL = 9


# ==========================================================
# Average True Range (ATR)
# ==========================================================

DEFAULT_ATR_PERIOD = 14


# ==========================================================
# Bollinger Bands
# ==========================================================

DEFAULT_BOLLINGER_WINDOW = 20

DEFAULT_BOLLINGER_STD = 2

# ==========================================================
# Bollinger Interpretation
# ==========================================================

ABOVE_UPPER_BAND = "Above Upper Band"

BELOW_LOWER_BAND = "Below Lower Band"

NEAR_UPPER_BAND = "Near Upper Band"

NEAR_LOWER_BAND = "Near Lower Band"

WITHIN_BANDS = "Within Bands"


# ==========================================================
# Trading Signals
# ==========================================================

BUY = "BUY"

SELL = "SELL"

HOLD = "HOLD"


# ==========================================================
# Trend Labels
# ==========================================================

BULLISH = "Bullish"

BEARISH = "Bearish"

NEUTRAL = "Neutral"

BULLISH_CROSSOVER = "Bullish Crossover"

BEARISH_CROSSOVER = "Bearish Crossover"