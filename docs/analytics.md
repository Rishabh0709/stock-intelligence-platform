# Analytics Engine

The analytics layer operates entirely on PriceSeries.

No calculator communicates with repositories or providers.

PriceSeries

↓

ReturnCalculator

↓

MovingAverageCalculator

↓

RSICalculator

↓

Future Indicators


Indicators inherit from IndicatorBase.

Current indicators

- SMA
- EMA
- RSI

Planned indicators

- MACD
- Bollinger Bands
- ATR
- ADX
- SuperTrend
- Ichimoku