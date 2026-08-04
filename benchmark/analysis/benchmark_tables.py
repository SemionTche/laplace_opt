from __future__ import annotations


import pandas as pd

from .benchmark_analysis import BenchmarkAnalysis


class BenchmarkTables:
    """
    Utilities to generate benchmark tables.
    """

    def __init__(self, analysis: BenchmarkAnalysis):

        self.analysis = analysis


    def runs(self):
        """
        One row per optimization run.
        """
        return (
            self.analysis.dataframe()
        )


    def comparison(self):
        """
        Mean/std comparison table.
        """
        df = self.runs()

        metrics = [

            "simple_regret",

            "auc_regret",

            "time_to_eps",

            "distance_x",

        ]

        table = (
            df.groupby(
                [
                    "function",
                    "strategy",
                    "acquisition"
                ]
            )[metrics]
            .agg(
                [
                    "mean",
                    "std"
                ]
            )
        )

        return table


    def ranking(self, metric="simple_regret"):
        """
        Rank strategies.

        Lower is better.
        """
        df = self.runs()

        ranking = (
            df
            .groupby(
                [
                    "strategy",
                    "acquisition"
                ]
            )[metric]
            .mean()
            .sort_values()
        )

        return ranking


    def formatted(self, metric="simple_regret"):

        df = self.runs()

        table = (
            df
            .groupby(
                [
                    "strategy",
                    "acquisition"
                ]
            )[metric]
            .agg(
                [
                    "mean",
                    "std"
                ]
            )
        )

        table["result"] = (
            table["mean"]
            .map(
                lambda x:
                f"{x:.3e}"
            )
            +
            " ± "
            +
            table["std"]
            .map(
                lambda x:
                f"{x:.3e}"
            )
        )

        return table[
            ["result"]
        ]


    def to_csv(self, path):

        self.comparison().to_csv(
            path
        )


    def to_latex(self, path):

        latex = (
            self.comparison()
            .to_latex()
        )

        with open(
            path,
            "w"
        ) as f:

            f.write(latex)