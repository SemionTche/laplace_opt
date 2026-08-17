from pathlib import Path

from .analysis import BenchmarkLoader, BenchmarkAnalysis
# from .analysis.benchmark_tables import BenchmarkTables


if __name__ == "__main__":

    root = Path(
        "benchmark/results/bench_test_09"
    )

    # load the data
    loader = BenchmarkLoader( root )

    # analyse the data
    analysis = BenchmarkAnalysis( loader )

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