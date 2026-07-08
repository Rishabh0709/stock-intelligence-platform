from functools import lru_cache


@lru_cache(maxsize=256)
def cached_symbol(symbol: str):

    return symbol.upper()