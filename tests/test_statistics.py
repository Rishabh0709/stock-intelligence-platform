import unittest

from src.analytics.statistics.statistics_calculator import StatisticsCalculator


class StatisticsCalculatorTests(unittest.TestCase):
    def test_static_statistics(self):
        values = [10, 12, 8, 15]
        self.assertEqual(StatisticsCalculator.mean(values), 11.25)
        self.assertAlmostEqual(StatisticsCalculator.variance(values), 6.6875)

    def test_rolling_mean_preserves_warmup(self):
        calculator = StatisticsCalculator([1, 2, 3, 4])
        self.assertEqual(calculator.rolling_mean(3), [None, None, 2.0, 3.0])

    def test_empty_values_are_rejected(self):
        with self.assertRaises(ValueError):
            StatisticsCalculator([])


if __name__ == "__main__":
    unittest.main()
