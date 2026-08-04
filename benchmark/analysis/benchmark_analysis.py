from __future__ import annotations


from pathlib import Path

import pandas as pd

from .benchmark_analyzer import BenchmarkAnalyzer
from ..benchmark_result import BenchmarkResult



class BenchmarkAnalysis:
    """
    Analysis of a complete benchmark campaign.

    Input:
        list[BenchmarkResult]
    """

    def __init__(self, results: list[BenchmarkResult]):

        self.results = results


    def dataframe(self) -> pd.DataFrame:
        """
        One row per optimization run.
        """
        rows = []

        for result in self.results:

            analyzer = BenchmarkAnalyzer(
                result
            )

            rows.append(
                analyzer.summary()
            )

        return pd.DataFrame(rows)


    def aggregate(
        self,
        group_by=[
            "function",
            "strategy",
            "acquisition",
        ]) -> pd.DataFrame:
        """
        Aggregate repeated seeds.

        Computes:
            mean
            std
        """

        df = self.dataframe()

        metrics = [
            "simple_regret",

            "auc_regret",

            "time_to_eps",

            "distance_x",
        ]

        grouped = (
            df
            .groupby(group_by)[metrics]
            .agg(
                [
                    "mean",
                    "std",
                ]
            )
        )

        return grouped


    def regret_curves(self):
        """
        Return regret history for every run.
        """
        curves = []

        for result in self.results:

            analyzer = BenchmarkAnalyzer(
                result
            )

            curves.append(
                {
                    "function":
                        result.function_name,

                    "strategy":
                        result.strategy,

                    "acquisition":
                        result.acquisition,

                    "seed":
                        result.seed,

                    "curve":
                        analyzer.regret_curve(),
                }
            )

        return curves


    def best_objective_curves(self):
        curves = []

        for result in self.results:

            analyzer = BenchmarkAnalyzer(
                result
            )

            curves.append(

                {
                    "function":
                        result.function_name,


                    "strategy":
                        result.strategy,


                    "seed":
                        result.seed,


                    "curve":
                        analyzer.best_curve(),
                }
            )

        return curves


    def save_summary(self, path: Path):

        df = self.dataframe()

        df.to_csv(
            path,
            index=False
        )


    def save_aggregate(self, path: Path):

        df = self.aggregate()

        df.to_csv(
            path
        )