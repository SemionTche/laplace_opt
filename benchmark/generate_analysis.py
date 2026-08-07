from pathlib import Path

from .analysis.benchmark_loader import BenchmarkLoader
from .analysis.benchmark_analysis import BenchmarkAnalysis
# from .analysis.benchmark_tables import BenchmarkTables


if __name__ == "__main__":

    root = Path(
        "benchmark/results/bench_test_07"
    )

    # load the data
    loader = BenchmarkLoader( root )
    results = loader.load()

    # analyse the data
    analysis = BenchmarkAnalysis( results )

    print()
    print("=" * 60)
    print("df:")
    print(analysis.df)
    print()
    print("=" * 60)
    print("aggregate:")
    print(analysis.agg)
    print()
    print("=" * 60)
    print()

    analysis.save_summary(
        path=root / "analysis_summary"
    )

    analysis.save_aggregate(
        path=root / "analysis_aggregate"
    )


    # make tables
    # tables = BenchmarkTables(
    #     analysis
    # )

    # print(
    #     tables.ranking()
    # )

    # print(
    #     tables.formatted()
    # )