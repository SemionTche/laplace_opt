from __future__ import annotations

from pathlib import Path
from collections import defaultdict
import numpy as np
import pandas as pd

from .benchmark_analyzer import BenchmarkAnalyzer
from ..experiment import BenchmarkResult
from ..metrics import METRICS
from ..bench_utils.normalize import norm_curve


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
        self.analyzers : list[BenchmarkAnalyzer] = []

        for result in results:
            self.analyzers.append( BenchmarkAnalyzer(result=result) )

        self.df = self.dataframe()
        self.agg = self.aggregate()
        self.curve_names = [
            # "best_curve",
            "regret_curve",
            # "regret_instantaneous",
            "noise_curve",
            "contraction_variance_curve",
            "contraction_entropy_curve",

            # "lengthscale_curve",
            # "contraction_variance_rate",
        ]
        print("Analysis generated.")


    def dataframe(self) -> pd.DataFrame:
        """Full analysis dataframe."""
        rows = []

        for a in self.analyzers:
            rows.append(a.summary())

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
        metrics = []
        for metric in METRICS.values():
            metrics.append(metric.name)
            if metric.relative_name is not None:
                metrics.append(metric.relative_name)

        grouped = (
            self.df.groupby(group_by)[metrics].agg(
                [
                    "mean",
                    "std",
                ]
            )
        )
        return grouped


    def curves(self,
               curve: str,
               *,
               normalization: str | None = None,
               reduction: str | None = None,
               groupby=("function",),):
        """
        Parameters
        ----------
        curve : str
            Name of the BenchmarkAnalyzer method.

        normalization
            None
            "relative"

        reduction
            None
            "mean"

        groupby
            Metadata used when averaging.
        """
        rows = []

        for analyzer in self.analyzers:

            values = getattr(analyzer, curve)()

            values = norm_curve(
                curve=values, 
                normalization=normalization
            )

            rows.append(
                {
                    "function": analyzer.result.function_name,
                    "strategy": analyzer.result.strategy,
                    "acquisition": analyzer.result.acquisition,
                    "seed": analyzer.result.seed,
                    "curve": values,
                }
            )

        if reduction is None:
            return rows

        if reduction != "mean":
            raise ValueError(f"Unknown reduction '{reduction}'")

        groups = defaultdict(list)

        for row in rows:
            key = tuple(row[k] for k in groupby)
            groups[key].append(row["curve"])

        output = []

        for key, curves in groups.items():

            d = dict(zip(groupby, key))
            d["curve"] = np.mean(np.stack(curves), axis=0)

            output.append(d)

        return output


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