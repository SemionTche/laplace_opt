from pathlib import Path
from matplotlib.axes import Axes
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from ..analysis import BenchmarkLoader, BenchmarkAnalysis

from .setter import set_axis


class PlotMaker():

    def __init__(self, root: Path):
            self.root = root

            # create the loader
            loader = BenchmarkLoader(root)

            self.analysis = BenchmarkAnalysis(loader=loader)

            self.analysis.save_summary(
                loader.root / "analysis_summary"
            )
            self.analysis.save_aggregate(
                path=loader.root / "analysis_aggregate"
            )


            n = len(self.analysis.curve_names)
            # fig, axs = plt.subplots(n, 4, figsize=(20, 10))

            # for i, name in enumerate(self.analysis.curve_names):
                 
            #     self.plot_curve(
            #         ax=axs[i, 0], 
            #         curve=name,
            #         normalization=None,
            #         reduction=None
            #     )
            #     self.plot_curve(
            #         ax=axs[i, 1], 
            #         curve=name, 
            #         normalization="relative", 
            #         reduction=None
            #     )
            #     self.plot_curve(
            #         ax=axs[i, 2], 
            #         curve=name, 
            #         normalization=None, 
            #         reduction="mean"
            #     )
            #     self.plot_curve(
            #         ax=axs[i, 3], 
            #         curve=name, 
            #         normalization="relative", 
            #         reduction="mean"
            #     )

            # fig, axs = plt.subplots(n, 2, figsize=(20, 10))

            # for i, name in enumerate(self.analysis.curve_names):
                 
            #     self.plot_curve(
            #         ax=axs[i, 0], 
            #         curve=name,
            #         normalization=None,
            #         reduction=None
            #     )
            #     self.plot_curve(
            #         ax=axs[i, 1], 
            #         curve=name, 
            #         normalization="relative", 
            #         reduction="mean"
            #     )

            # fig.tight_layout()
            # plt.show()


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


    def make_indiv_plots(self,
                        *,
                        normalization: str | None = None,
                        save: bool = False,
                        show: bool = True,
                        output_folder: str = "figures") -> None:
        """
        Create one figure per curve and per test function.

        Each figure contains only the different seeds belonging
        to the corresponding test function.

        Args:
            normalization (str | None)
                None or "relative".

            save (bool)
                If True, figures are saved under:
                    
                    benchmark root/figures/function/curve.png

            show (bool)
                If True, display the figures with matplotlib.

            output_folder (str)
                Name of the folder created in the benchmark directory.
        """
        if normalization not in (None, "relative"):
            raise ValueError(
                f"Unknown normalization '{normalization}'. "
                "Expected None or 'relative'."
            )

        # Create output directory if necessary
        if save:
            output_root = self.root / output_folder
            output_root.mkdir(parents=True, exist_ok=True)

        # Find all functions
        functions = sorted(
            { record.function for record in self.analysis.records }
        )

        # One function -> one directory
        # One curve -> one figure
        for function in functions:

            if save:
                function_folder = output_root / function
                function_folder.mkdir( parents=True, exist_ok=True )

            for curve_name in self.analysis.curve_names:

                fig, ax = plt.subplots(
                    figsize=(10, 6)
                )

                # Get all curves for this particular curve.
                curves = self.analysis.curves(
                    curve=curve_name,
                    normalization=normalization,
                    reduction=None,
                )

                # Keep only this test function.
                curves = [
                    c for c in curves if c["function"] == function
                ]

                # Plot seeds
                for c in curves:
                    ax.plot( c["curve"], label=f"seed {c['seed']}" )

                # Axis
                if normalization == "relative":
                    curve_name = curve_name + "_relative"
                title = f"{function} — {curve_name}"
                set_axis( ax=ax, xlabel="iterations", title=title )

                ax.legend()
                fig.tight_layout()

                # save
                if save:
                    filename = curve_name + ".png"
                    fig.savefig(
                        function_folder / filename,
                        dpi=300,
                        bbox_inches="tight",
                    )

                # show
                if show:
                    plt.show()

                # close the figure.
                plt.close(fig)


    def make_average_plots(self,
                           *,
                           normalization: str | None = None,
                           save: bool = False,
                           show: bool = True,
                           output_folder: str = "figures",
                           average_folder: str = "averaged",
                           show_std: bool = True):
        """
        Create one figure per curve, averaging over seeds.

        For each curve, one line is plotted for each test function.
        The line corresponds to the mean over all seeds of that function.

        If ``show_std`` is True, a shaded region corresponding to
        mean +/- standard deviation is displayed.

        Args:
            normalization:
                None or "relative".

            save:
                If True, save figures under:

                    <benchmark root>/<output_folder>/<average_folder>/

            show:
                If True, display the figures with matplotlib.

            output_folder:
                Main figure output directory.

            average_folder:
                Subdirectory containing the averaged plots.

            show_std:
                If True, show mean +/- standard deviation as a shaded area.
        """
        if normalization not in (None, "relative"):
            raise ValueError(
                f"Unknown normalization '{normalization}'. "
                "Expected None or 'relative'."
            )

        # Create output directory
        if save:

            output_root = ( self.root / output_folder / average_folder )
            output_root.mkdir( parents=True, exist_ok=True )

        # Find test functions
        functions = sorted(
            { record.function for record in self.analysis.records }
        )

        # One figure per curve
        for curve_name in self.analysis.curve_names:

            curves = self.analysis.curves(
                curve=curve_name,
                normalization=normalization,
                reduction=None,
            )

            fig, ax = plt.subplots(
                figsize=(10, 6)
            )

            # One averaged curve per test function
            for function in functions:

                function_curves = [
                    c["curve"] for c in curves if c["function"] == function
                ]

                if not function_curves:
                    continue

                values = np.stack( function_curves )

                mean = np.mean( values, axis=0 )

                std = np.std( values, axis=0 )

                # Plot mean
                line = ax.plot( mean, label=function, )[0]

                # Plot standard deviation
                if show_std:
                    ax.fill_between(
                        np.arange(len(mean)),
                        mean - std,
                        mean + std,
                        alpha=0.2,
                        color=line.get_color(),
                    )

            # Formatting
            if normalization == "relative":
                curve_name += "_relative"
            title = f"{curve_name} — averaged over seeds"

            set_axis( ax=ax, xlabel="iterations", title=title, )

            ax.legend()
            fig.tight_layout()

            # Save
            if save:

                filename = curve_name + ".png"

                fig.savefig(
                    output_root / filename,
                    dpi=300,
                    bbox_inches="tight",
                )

            # Show / cleanup
            if show:
                plt.show()

            plt.close(fig)


if __name__ == "__main__":
    root = Path("benchmark/results/bench_test_08")
    pm = PlotMaker(root)
