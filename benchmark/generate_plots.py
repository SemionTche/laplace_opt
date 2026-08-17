from pathlib import Path

from .plotting import PlotMaker


if __name__ == "__main__":
    
    root = Path(
        "benchmark/results/bench_test_08"
    )

    pm = PlotMaker(root)

    pm.make_indiv_plots(
        save=True,
        show=False
    )

    pm.make_average_plots(
        normalization="relative",
        save=True,
        show=True
    )