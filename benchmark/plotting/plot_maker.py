from pathlib import Path
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd

from ..analysis import BenchmarkLoader, BenchmarkAnalysis

from .setter import set_axis


class PlotMaker():

    def __init__(self, root: Path):
            # load the data
            loader = BenchmarkLoader(root)
            results = loader.load()

            self.analisis = BenchmarkAnalysis(results=results)

            self.df = self.analisis.df
            self.agg = self.analisis.aggregate()

            fig, axs = plt.subplots(1, 1, figsize=(8, 8))

            axs = self.plot_regret(ax=axs)

            fig.tight_layout()
            plt.show()


    def plot_regret(self, ax: Axes) -> Axes:
        curves = self.analisis.regret_curves()

        for curve in curves:
             label = f"{curve['function']} seed {curve['seed']}"
             ax.plot(curve["curve"], label=label)

        ax.legend()
        return ax



if __name__ == "__main__":
    root = Path("benchmark/results/bench_test_08")
    pm = PlotMaker(root)
