from src.analytics.statistics.statistics_calculator import (
    StatisticsCalculator,
)

values = [10, 12, 8, 15, 20, 18, 22]

stats = StatisticsCalculator(values)

print("Count      :", stats.count())
print("Mean       :", stats.mean())
print("Median     :", stats.median())
print("Minimum    :", stats.minimum())
print("Maximum    :", stats.maximum())
print("Range      :", stats.range())
print("Variance   :", stats.variance())
print("Std Dev    :", stats.standard_deviation())
print("Coeff Var  :", stats.coefficient_of_variation())
print("RMS        :", stats.rms())
print("90th %ile  :", stats.percentile(90))