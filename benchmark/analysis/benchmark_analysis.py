from __future__ import annotations


from pathlib import Path

import pandas as pd

from .benchmark_analyzer import BenchmarkAnalyzer
from ..benchmark_result import BenchmarkResult
from ..metrics import METRICS


class BenchmarkAnalysis:
    """
    Analysis of a complete benchmark campaign.
    """

    def __init__(self, results: list[BenchmarkResult]):
        """
        Args:
            result (list[BenchmarkResult]):
                The benchmark list of results to study.
        """
        self.results = results

        self.df = self.dataframe()
        self.agg = self.aggregate()
        print("Analysis generated.")


    def dataframe(self) -> pd.DataFrame:
        """
        Full analysis dataframe.
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


    def aggregate(self,
                  group_by=[
                      "function",
                      "strategy",
                      "acquisition",]) -> pd.DataFrame:
        """
        Aggregate the relevant features.

        Computes:
            mean and std
        """
        df = self.dataframe()
        metrics = [metric.name for metric in METRICS.values()]
        grouped = (
            df.groupby(group_by)[metrics].agg(
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


    def save_summary(self, path: Path) -> None:
        """Save the full analysis summary."""
        self.df.to_csv(path.with_suffix(".csv"), index=False)
        self.df.to_html(path.with_suffix(".htlm"))
        print("DataFrame saved.")


    def save_aggregate(self, path: Path) -> None:
        """Save the full analysis aggregate."""
        self.agg.to_csv(path.with_suffix(".csv"))
        self.agg.to_html(path.with_suffix(".htlm"))
        print("Aggregate saved.")