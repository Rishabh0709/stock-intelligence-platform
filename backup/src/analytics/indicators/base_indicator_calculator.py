import pandas as pd

from src.analytics.core.price_series import PriceSeries


class BaseIndicatorCalculator:

    def __init__(self, series: PriceSeries):
        self.series = series

    @property
    def dataframe(self):
        return self.series.dataframe.copy()

    @staticmethod
    def normalize_date(value):
        if isinstance(value, pd.Timestamp):
            return value.date()
        return value

    @staticmethod
    def to_float(value):
        if pd.isna(value):
            return None
        return float(value)