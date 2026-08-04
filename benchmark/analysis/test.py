from pathlib import Path

from .benchmark_loader import BenchmarkLoader
from .benchmark_analysis import BenchmarkAnalysis
from .benchmark_tables import BenchmarkTables

root = Path("benchmark/results/bench_test_01")


loader = BenchmarkLoader(
    root
)

results = loader.load()


analysis = BenchmarkAnalysis(
    results
)

analysis.save_summary(
    path=root / "analysis_summary.csv"
)

analysis.save_aggregate(
    path=root / "analysis_aggregate.csv"
)


tables = BenchmarkTables(
    analysis
)


print(
    tables.ranking()
)


print(
    tables.formatted()
)