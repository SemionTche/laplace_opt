from pathlib import Path

from .benchmark_loader import BenchmarkLoader
from .benchmark_analysis import BenchmarkAnalysis
from .benchmark_tables import BenchmarkTables


if __name__ == "__main__":

    root = Path(
        "benchmark/results/bench_test_01"
    )

    # load the data
    loader = BenchmarkLoader(
        root
    )
    results = loader.load()


    # analyse the data
    analysis = BenchmarkAnalysis(
        results
    )

    print()
    print("=" * 60)
    print("df:")
    print(analysis.dataframe())
    print()
    print("=" * 60)
    print("aggregate:")
    print(analysis.aggregate())
    print()
    print("=" * 60)
    print()

    analysis.save_summary(
        path=root / "analysis_summary.csv"
    )

    analysis.save_aggregate(
        path=root / "analysis_aggregate.csv"
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