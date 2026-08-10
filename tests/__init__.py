"""Test-suite dependency isolation.

Unit tests patch indicator outputs and should not import numba or execute the
real pandas-ta implementation. Provider integration belongs in a separate,
explicit test command.
"""

import sys
from types import ModuleType


if "pandas_ta" not in sys.modules:
    pandas_ta_stub = ModuleType("pandas_ta")
    for function_name in (
        "adx",
        "atr",
        "bbands",
        "ema",
        "macd",
        "rsi",
        "sma",
        "true_range",
    ):
        setattr(pandas_ta_stub, function_name, lambda *args, **kwargs: None)
    sys.modules["pandas_ta"] = pandas_ta_stub
