"""
Centralized scoring weights.

Changing these values changes the behavior of the
StockScoreEngine without modifying any rule.
"""

# ===============================
# Trend
# ===============================

STRONG_BULLISH_TREND = 25
WEAK_BULLISH_TREND = 15

STRONG_BEARISH_TREND = -25
WEAK_BEARISH_TREND = -15

SIDEWAYS_TREND = 0


# ===============================
# Momentum
# ===============================

BULLISH_MACD = 10
BEARISH_MACD = -10

RSI_HEALTHY = 8
RSI_OVERSOLD = 5
RSI_OVERBOUGHT = -8

NEUTRAL_MOMENTUM = 0


# ===============================
# Volatility
# ===============================

LOW_VOLATILITY = 8
MEDIUM_VOLATILITY = 4
HIGH_VOLATILITY = -6

NEAR_LOWER_BAND = 5
NEAR_UPPER_BAND = -5


# ===============================
# Risk
# ===============================

LOW_RISK = 12
MEDIUM_RISK = 5
HIGH_RISK = -12

HEALTHY_DRAWDOWN = 5
NORMAL_DRAWDOWN = 2
DEEP_DRAWDOWN = -5
SEVERE_DRAWDOWN = -10