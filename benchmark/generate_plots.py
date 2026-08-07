from pathlib import Path

from .plotting import PlotMaker


if __name__ == "__main__":
    
    root = Path(
        "benchmark/results/bench_test_09"
    )

    pm = PlotMaker(root)