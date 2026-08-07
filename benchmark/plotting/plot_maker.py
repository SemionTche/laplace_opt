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

            self.analysis = BenchmarkAnalysis(results=results)

            self.df = self.analysis.df
            self.agg = self.analysis.aggregate()
            n = len(self.analysis.curve_names)
            fig, axs = plt.subplots(n, 4, figsize=(20, 10))

            for i, name in enumerate(self.analysis.curve_names):
                 
                self.plot_curve(
                    ax=axs[i, 0], 
                    curve=name,
                    normalization=None,
                    reduction=None
                )
                self.plot_curve(
                    ax=axs[i, 1], 
                    curve=name, 
                    normalization="relative", 
                    reduction=None
                )
                self.plot_curve(
                    ax=axs[i, 2], 
                    curve=name, 
                    normalization=None, 
                    reduction="mean"
                )
                self.plot_curve(
                    ax=axs[i, 3], 
                    curve=name, 
                    normalization="relative", 
                    reduction="mean"
                )
            

            fig.tight_layout()
            plt.show()


    def plot_curve(self,
                   ax: Axes,
                   curve: str,
                   *,
                   normalization: str | None = None,
                   reduction: str | None = None):

        curves = self.analysis.curves(
            curve=curve,
            normalization=normalization,
            reduction=reduction,
        )

        for c in curves:

            if reduction is None:
                label = f"{c['function']} seed {c['seed']}"
            else:
                label = c["function"]

            ax.plot(c["curve"], label=label)

        set_axis(ax=ax, xlabel="iterations", title=f"{curve}")

        ax.legend()



if __name__ == "__main__":
    root = Path("benchmark/results/bench_test_08")
    pm = PlotMaker(root)
